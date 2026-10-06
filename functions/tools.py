#    This file is part of the AutoAnime distribution.
#    Copyright (c) 2026 Kaif_00z
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
# License can be found in <
# https://github.com/kaif-00z/AutoAnimeBot/blob/main/LICENSE > .

# if you are using this following code then don't forgot to give proper
# credit to t.me/kAiF_00z (github.com/kaif-00z)

import asyncio
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import time
from traceback import format_exc

import aiofiles
import aiohttp
import requests
from html_telegraph_poster import TelegraphPoster
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from functions.config import Var
from libs.logger import LOGS


class Tools:
    def __init__(self):
        pass

    async def async_searcher(
        self,
        url: str,
        post: bool = None,
        headers: dict = None,
        params: dict = None,
        json: dict = None,
        data: dict = None,
        ssl=None,
        re_json: bool = False,
        re_content: bool = False,
        real: bool = False,
        *args,
        **kwargs,
    ):
        async with aiohttp.ClientSession(headers=headers) as client:
            if post:
                data = await client.post(
                    url, json=json, data=data, ssl=ssl, *args, **kwargs
                )
            else:
                data = await client.get(url, params=params, ssl=ssl, *args, **kwargs)
            if re_json:
                return await data.json()
            if re_content:
                return await data.read()
            if real:
                return data
            return await data.text()

    async def cover_dl(self, link):
        try:
            if not link:
                return None
            image = await self.async_searcher(link, re_content=True)
            clean_link = link.split("?")[0]
            filename = clean_link.split("/")[-1]
            if len(filename) > 30 or not filename.lower().endswith(
                (".jpg", ".png", ".jpeg")
            ):
                filename = hashlib.md5(link.encode()).hexdigest() + ".jpg"
            fn = f"thumbs/{filename}"
            async with aiofiles.open(fn, "wb") as file:
                await file.write(image)
            return fn
        except Exception as error:
            LOGS.exception(format_exc())
            LOGS.error(str(error))

    async def mediainfo(self, file, bot):
        try:
            process = await asyncio.create_subprocess_exec(
                "mediainfo",
                file,
                "--Output=HTML",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            out = stdout.decode()
            client = TelegraphPoster(use_api=True)
            client.create_api_token("Mediainfo")
            page = client.post(
                title="Mediainfo",
                author=((await bot.get_me()).first_name),
                author_url=f"https://t.me/{((await bot.get_me()).username)}",
                text=out,
            )
            return page.get("url")
        except Exception as error:
            LOGS.exception(format_exc())
            LOGS.error(str(error))

    async def _poster(self, bot, anime_info, channel_id=None):
        thumb = await self.cover_dl((await anime_info.get_cover()))
        caption = await anime_info.get_caption()
        return await bot.upload_poster(
            thumb or "assest/poster_not_found.jpg",
            caption,
            channel_id if channel_id else None,
        )

    async def get_chat_info(self, bot, anime_info, dB):
        try:
            chat_info = await dB.get_anime_channel_info(anime_info.proper_name)
            if not chat_info:
                chat_id = await bot.create_channel(
                    (await anime_info.get_english()),
                    (await self.cover_dl((await anime_info.get_poster()))),
                )
                invite_link = await bot.generate_invite_link(chat_id)
                chat_info = {"chat_id": chat_id, "invite_link": invite_link}
                await dB.add_anime_channel_info(anime_info.proper_name, chat_info)
            return chat_info
        except BaseException:
            LOGS.error(str(format_exc()))

    def init_dir(self):
        if not os.path.exists("thumb.jpg"):
            content = requests.get(Var.THUMB).content
            with open("thumb.jpg", "wb") as f:
                f.write(content)
        if not os.path.isdir("encode/"):
            os.mkdir("encode/")
        if not os.path.isdir("thumbs/"):
            os.mkdir("thumbs/")
        if not os.path.isdir("downloads/"):
            os.mkdir("downloads/")

    def hbs(self, size):
        if not size:
            return ""
        power = 2**10
        raised_to_pow = 0
        dict_power_n = {0: "B", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}
        while size > power:
            size /= power
            raised_to_pow += 1
        return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"

    def ts(self, milliseconds: int) -> str:
        seconds, milliseconds = divmod(int(milliseconds), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        tmp = (
            ((str(days) + "d:") if days else "")
            + ((str(hours) + "h:") if hours else "")
            + ((str(minutes) + "m:") if minutes else "")
            + ((str(seconds) + "s:") if seconds else "")
            + ((str(milliseconds) + "ms:") if milliseconds else "")
        )
        return tmp[:-1]

    async def rename_file(self, dl, out):
        try:
            os.rename(dl, out)
        except BaseException:
            return False, format_exc()
        return True, out

    async def bash_(self, *cmd):
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        err = stderr.decode().strip() or None
        out = stdout.decode().strip()
        return out, err

    async def frame_counts(self, dl):
        try:
            output, _ = await self.bash_("mediainfo", "--fullscan", dl)
            if output:
                match = re.search(r"Frame count\s*:\s*([\d,]+)", output)
                if match:
                    return int(match.group(1).replace(",", ""))
        except Exception as e:
            LOGS.error(f"mediainfo frame count failed: {e}")

        try:
            output, _ = await self.bash_(
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-count_packets",
                "-show_entries",
                "stream=nb_read_packets",
                "-of",
                "csv=p=0",
                dl,
            )
            output = output.strip()
            if output.isdigit():
                return int(output)
        except Exception:
            pass

        try:
            duration = await self.genss(dl)
            if duration and duration > 0:
                return int(duration * 23.976)
        except Exception:
            pass

        return 27000

    async def compress(self, dl, out, log_msg):
        total_frames = await self.frame_counts(dl)
        if not total_frames:
            return False, "Unable to Count The Frames!"
        _progress = f"progress-{int(time.time() * 1000)}.txt"
        cmd = [
            Var.FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-progress",
            _progress,
            "-i",
            dl,
            "-metadata",
            "Encoded By=https://github.com/kaif-00z/AutoAnimeBot/",
            "-preset",
            "ultrafast",
            "-c:v",
            "libx265",
            "-crf",
            str(Var.CRF),
            "-vf",
            "crop=trunc(iw/2)*2:trunc(ih/2)*2",
            "-map",
            "0:v",
            "-c:a",
            "aac",
            "-map",
            "0:a",
            "-c:s",
            "copy",
            "-map",
            "0:s?",
            out,
            "-y",
        ]
        process = None
        latest_log_msg = log_msg
        start_time = time.time()
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            elapsed_frames = 0

            # None means the process is still running. Any exit code, including a
            # nonzero failure code, ends this loop and is checked below.
            while process.returncode is None:
                await asyncio.sleep(5)
                if (
                    time.time() - start_time > 60
                    and (not os.path.exists(out) or os.path.getsize(out) == 0)
                ):
                    process.kill()
                    await process.wait()
                    return False, "FFmpeg timed out before producing output."

                if not os.path.exists(_progress):
                    continue
                try:
                    with open(_progress, "r", encoding="utf-8") as progress_file:
                        progress_text = progress_file.read()
                except OSError:
                    continue

                frames = re.findall(r"frame=(\d+)", progress_text)
                sizes = re.findall(r"total_size=(\d+)", progress_text)
                if frames:
                    elapsed_frames = int(frames[-1])
                if not frames or not sizes:
                    continue

                output_size = int(sizes[-1])
                percent = min(100.0, elapsed_frames * 100 / total_frames)
                elapsed_seconds = max(time.time() - start_time, 1)
                frame_rate = elapsed_frames / elapsed_seconds
                if frame_rate <= 0:
                    continue

                eta_ms = max(0, (total_frames - elapsed_frames) / frame_rate * 1000)
                filled_blocks = min(20, max(0, math.floor(percent / 5)))
                progress_bar = "`[{0}{1}] {2:.2f}%\n\n`".format(
                    "●" * filled_blocks,
                    " " * (20 - filled_blocks),
                    percent,
                )
                estimated_size = output_size * 100 / max(percent, 0.01)
                status = (
                    f"**Successfully Downloaded The Anime**\n\n"
                    f"**File Name:** ```{os.path.basename(dl)}```\n\n"
                    f"**STATUS:** \n{progress_bar}"
                    f"`{self.hbs(output_size)} of ~{self.hbs(estimated_size)}`"
                    f"\n\n`~{self.ts(eta_ms)}`"
                )
                try:
                    latest_log_msg = await log_msg.edit(status)
                except MessageNotModifiedError:
                    pass

            return_code = await process.wait()
            if return_code != 0:
                return False, f"FFmpeg exited with status {return_code}."
            if not os.path.exists(out) or os.path.getsize(out) == 0:
                return False, "FFmpeg completed without producing a non-empty output."
            return True, latest_log_msg
        except Exception as error:
            if process and process.returncode is None:
                process.kill()
                await process.wait()
            LOGS.error(f"FFmpeg execution failed: {error}")
            return False, str(error)
        finally:
            try:
                os.remove(_progress)
            except OSError:
                pass

    async def genss(self, file):
        try:
            process = subprocess.Popen(
                [shutil.which("mediainfo"), file, "--Output=JSON"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            stdout, stderr = process.communicate()
            out = stdout.decode().strip()
            z = json.loads(out)

            tracks = z.get("media", {}).get("track")
            if not tracks:
                tracks = []

            duration_str = None
            for track in tracks:
                if track and "Duration" in track:
                    duration_str = str(track["Duration"])
                    break

            if duration_str:
                try:
                    return int(float(duration_str))
                except Exception:
                    pass
                if "." in duration_str:
                    try:
                        return int(duration_str.split(".")[0])
                    except Exception:
                        pass

            try:
                proc = subprocess.Popen(
                    [
                        shutil.which("ffprobe"),
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        file,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                stdout, _ = proc.communicate()
                f_dur = stdout.decode().strip()
                if f_dur:
                    return int(float(f_dur))
            except Exception:
                pass
        except Exception as e:
            LOGS.error(f"[genss] Error parsing duration: {e}")

        return 1140  # assume 19 min playback duration

    def stdr(self, seconds: int) -> str:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if len(str(minutes)) == 1:
            minutes = "0" + str(minutes)
        if len(str(hours)) == 1:
            hours = "0" + str(hours)
        if len(str(seconds)) == 1:
            seconds = "0" + str(seconds)
        dur = (
            ((str(hours) + ":") if hours else "00:")
            + ((str(minutes) + ":") if minutes else "00:")
            + ((str(seconds)) if seconds else "")
        )
        return dur

    async def duration_s(self, file):
        tsec = await self.genss(file)
        x = round(tsec / 5)
        y = round(tsec / 5 + 30)
        pin = self.stdr(x)
        if y < tsec:
            pon = self.stdr(y)
        else:
            pon = self.stdr(tsec)
        return pin, pon

    async def gen_ss_sam(self, _hash, filename):
        try:
            ss_path, sp_path = None, None
            os.mkdir(_hash)
            tsec = await self.genss(filename)
            fps = 10 / tsec
            process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-i",
                filename,
                "-vf",
                f"fps={fps}",
                "-vframes",
                "10",
                f"{_hash}/pic%01d.png",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()
            ss, dd = await self.duration_s(filename)
            out = f"{os.path.splitext(filename)[0]}_sample.mkv"
            process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-i",
                filename,
                "-preset",
                "ultrafast",
                "-ss",
                ss,
                "-to",
                dd,
                "-c:v",
                "libx265",
                "-crf",
                "27",
                "-map",
                "0:v",
                "-c:a",
                "aac",
                "-map",
                "0:a",
                "-c:s",
                "copy",
                "-map",
                "0:s?",
                out,
                "-y",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate()
            er = stderr.decode().strip()
            if process.returncode != 0 or not os.path.exists(out):
                LOGS.error(er or "FFmpeg failed to create the sample video.")
                return ss_path, sp_path
            return _hash, out
        except Exception as error:
            LOGS.error(str(error))
            LOGS.exception(format_exc())
