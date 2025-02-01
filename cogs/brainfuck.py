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

    @util.store_command()
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
        state.stop = True
        for e in state.errors:
            raise e
        if (len(state.timelines) > 0):
            await ctx.send("warning: program did not terminate within time limit")
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
        self.stop = False
        self.timelines = [Timeline(self, 0, [0], {})]
        self.errors: list[Exception] = []
        start_timeline(self.timelines[0])


class Timeline:
    def __init__(self, state: ProgramState, ip: int, mps: list[int], mem: dict[int, int]) -> None:
        self.state = state
        self.ip = ip
        self.mps = mps.copy()
        self.mem = mem.copy()
        self.history: list[tuple[tuple[int, int], ...]] = []
        self.mp_lock = threading.Lock()  # a lock wwhich is released only if this timeline has no memory pointers


def start_timeline(tl: Timeline) -> None:
    threading.Thread(target=run_timeline, args=(tl,)).start()


bracket1 = {"[": 1, "]": -1}
bracket2 = {"(": 1, ")": -1}


def run_timeline(tl: Timeline) -> None:
    try:
        while not tl.state.stop and tl.ip >= 0 and tl.ip < len(tl.state.program):
            if (len(tl.mps) and not tl.mp_lock.locked()):
                tl.mp_lock.acquire()
            elif (not len(tl.mps) and tl.mp_lock.locked()):
                tl.mp_lock.release()
            op = tl.state.program[tl.ip]
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
                    tl.state.output.write((tl.mem.get(p, 0)).to_bytes(1, "little"))
            elif op == ",":
                past: list[tuple[int, int]] = []
                c = (tl.state.input.read(1) or b"\xFF")[0]
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
                    while count and tl.ip < len(tl.state.program) - 1:
                        tl.ip += 1
                        count += bracket1.get(tl.state.program[tl.ip], 0)
            elif op == "]":
                jump = False
                for p in tl.mps:
                    if (tl.mem.get(p, 0)):
                        jump = True
                if (jump):
                    count = -1
                    while count and tl.ip >= 1:
                        tl.ip -= 1
                        count += bracket1.get(tl.state.program[tl.ip], 0)
            elif op == "~":
                if (len(tl.history) == 0):
                    raise interactions.errors.BadArgument("no history to rewind")
                step = tl.history.pop()
                for p, c in step:
                    tl.mem[p] = c
            elif op == "(":
                if (len(tl.state.timelines) >= 10):
                    raise interactions.errors.BadArgument("exceeded max (10) timelines")
                new_tl = Timeline(tl.state, tl.ip + 1, tl.mps.copy(), tl.mem.copy())
                tl.state.timelines.append(new_tl)
                start_timeline(new_tl)
                count = 1
                while count and tl.ip < len(tl.state.program) - 1:
                    tl.ip += 1
                    count += bracket2.get(tl.state.program[tl.ip], 0)
            elif op == ")":
                main = tl.state.timelines.index(tl) == 0
                if not main:
                    break
            elif op == "v":
                idx = tl.state.timelines.index(tl)
                try:
                    for p in tl.mps:
                        tl.state.timelines[idx + 1].mps.append(p)
                except IndexError:
                    pass
                tl.mps.clear()
            elif op == "^":
                idx = tl.state.timelines.index(tl)
                try:
                    for p in tl.mps:
                        tl.state.timelines[idx - 1].mps.append(p)
                except IndexError:
                    pass
                tl.mps.clear()
            elif op == "@":
                idx = tl.state.timelines.index(tl)
                try:
                    tl.state.timelines[idx+ 1].mp_lock.acquire()
                    tl.state.timelines[idx+ 1].mp_lock.release()
                except IndexError:
                    pass
            tl.ip += 1
        main = tl.state.timelines.index(tl) == 0
        tl.state.timelines.remove(tl)
        if main:
            tl.state.stop = True
        if (tl.mp_lock.locked()):
            tl.mp_lock.release()
    except Exception as e:
        tl.state.errors.append(e)
