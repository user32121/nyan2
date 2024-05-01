import asyncio
import io
import logging
import threading
import typing

import interactions

import util

logger = logging.getLogger(__name__)


class Brainfuck(interactions.Extension):
    def __init__(self, bot) -> None:
        logger.info("init")

    @interactions.slash_command(** util.command_args, name="brainfuck", description="run a brainfuck program (10 second time limit)")
    async def brainfuck(self, ctx: interactions.SlashContext,
                        program: typing.Annotated[str, interactions.slash_str_option("instructions to run", True)],
                        input: typing.Annotated[str, interactions.slash_str_option("input to pass to the program")] = "",
                        ) -> None:
        await util.preprocess(ctx)
        state = ProgramState(program, io.BytesIO(input.encode()), io.BytesIO())
        for _ in range(10):
            if (len(state.timelines) == 0):
                break
            await asyncio.sleep(1)
        state.force_stop = True
        for e in state.errors:
            raise e
        if (len(state.timelines) > 0):
            raise interactions.errors.BadArgument("program did not terminate within time limit")
        if (state.output.tell() == 0):
            await ctx.send("no output")
        else:
            state.output.seek(0)
            await ctx.send(f"output: ```{state.output.read()}```")


class ProgramState:
    def __init__(self, program: str, input: typing.BinaryIO, output: typing.BinaryIO) -> None:
        self.program = program
        self.input = input
        self.output = output
        self.force_stop = False
        self.timelines = [Timeline(self, 0, [0], {})]
        self.errors: list[Exception] = []
        startTimeline(self.timelines[0])


class Timeline:
    def __init__(self, state: ProgramState, ip: int, mps: list[int], mem: dict[int, int]) -> None:
        self.parent = state
        self.ip = ip
        self.mps = mps.copy()
        self.mem = mem.copy()
        self.history: list[tuple[tuple[int, int], ...]] = []


def startTimeline(tl: Timeline) -> None:
    threading.Thread(target=runTimeline, args=(tl,)).start()


bracket1 = {"[": 1, "]": -1}
bracket2 = {"(": 1, ")": -1}


def runTimeline(tl: Timeline) -> None:
    try:
        while not tl.parent.force_stop and tl.ip >= 0 and tl.ip < len(tl.parent.program):
            op = tl.parent.program[tl.ip]
            if op == ">":
                for i in range(len(tl.mps)):
                    tl.mps[i] += 1
            elif op == "<":
                for i in range(len(tl.mps)):
                    tl.mps[i] -= 1
            elif op == "+":
                past: list[tuple[int, int]] = []
                for p in tl.mps:
                    past.append((p, tl.mem.get(p, 0)))
                    tl.mem[p] = (tl.mem.get(p, 0) + 1) % 256
                tl.history.append(tuple(past))
            elif op == "-":
                past: list[tuple[int, int]] = []
                for p in tl.mps:
                    past.append((p, tl.mem.get(p, 0)))
                    tl.mem[p] = (tl.mem.get(p, 0) - 1) % 256
                tl.history.append(tuple(past))
            elif op == ".":
                for p in tl.mps:
                    tl.parent.output.write((tl.mem.get(p, 0)).to_bytes(1, "little"))
            elif op == ",":
                past: list[tuple[int, int]] = []
                c = (tl.parent.input.read(1) or b"\xFF")[0]
                for p in tl.mps:
                    past.append((p, tl.mem.get(p, 0)))
                    tl.mem[p] = c
                tl.history.append(tuple(past))
            elif op == "[":
                jump = True
                for p in tl.mps:
                    if (tl.mem.get(p, 0)):
                        jump = False
                if (jump):
                    count = 1
                    tl.ip += 1
                    while count and tl.ip < len(tl.parent.program):
                        count += bracket1.get(tl.parent.program[tl.ip], 0)
                        tl.ip += 1
                    tl.ip -= 1
            elif op == "]":
                jump = False
                for p in tl.mps:
                    if (tl.mem.get(p, 0)):
                        jump = True
                if (jump):
                    count = -1
                    tl.ip -= 1
                    while count and tl.ip >= 0:
                        count += bracket1.get(tl.parent.program[tl.ip], 0)
                        tl.ip -= 1
                    tl.ip += 1
            tl.ip += 1
        tl.parent.timelines.remove(tl)
    except Exception as e:
        tl.parent.errors.append(e)
