# coding: utf-8
#

import time
from collections import namedtuple

import cv2
import numpy as np
from PIL import Image
from logzero import logger
import io
import re
import requests
import functools

MatchResult = namedtuple(
    'MatchResult', ['pos', 'center', 'val', 'image', 'template'])


def convert2opencv(im):
    """ 将im对象转化为OpenCV.Image """
    if isinstance(im, Image.Image):
        im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        return cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    if isinstance(im, str):
        if re.match(r"^https?://", im):
            resp = requests.get(im)
            nparr = np.frombuffer(resp.content, np.uint8)
            im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
            # return Image.open(io.BytesIO(resp.content))
        return cv2.imread(im, 0)
    if isinstance(im, (np.ndarray, np.generic)):
        return im
    raise ValueError("Unknown type", type(im))


def findit(logo, background):
    """ 确定目标元素的位置 """
    logo = convert2opencv(logo)
    background = convert2opencv(background)

    res = cv2.matchTemplate(logo, background, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    w, h = logo.shape[::-1]
    x, y = (top_left[0] + w//2, top_left[1] + h//2)
    return MatchResult(top_left, (x, y), max_val, logo, background)


_RETRY = "1"
_ABORT = "2"
_CONTINUE = "3"
_RECAPTURE = "4"


def promptable(fn):
    @functools.wraps(fn)
    def inner(self, im, *args, **kwargs):
        self._depth += 1
        try:
            ret = fn(self, im, *args, **kwargs)
            return ret
        except RuntimeError:
            if self._debug and self._depth == 1:
                val = input("1. Retry 2. Abort [1]? ")
                if val == "1":
                    return fn(self, im, *args, **kwargs)
            raise
        finally:
            self._depth -= 1

    return inner


class CVToolKit():
    def __init__(self):
        self._screenshot = None
        self._click = None
        self._debug = True
        self._depth = 0

    @promptable
    def find(self, im):
        """
        Returns:
            (res, bool): result and bool about if matched
        """
        screenshot = self._screenshot()
        res = findit(im, screenshot)
        self.debugf("Match(%s) val:%.1f, pos:%s", im, res.val, res.pos)
        if res.val > 0.9:
            return res, True
        return res, False

    @promptable
    def wait(self, im, timeout: float = 10.0):
        self.debugf("WAIT: %s", im)
        deadline = time.time() + timeout
        while time.time() < deadline:
            res, ok = self.find(im)
            if ok:
                self.debugf("Matched: val(%.1f)", res.val)
                return res
            time.sleep(.2)
        raise RuntimeError("wait timeout")

    @promptable
    def click(self, im):
        res = self.wait(im)
        x, y = res.center
        self.debugf("TARGET: %d, %d, matchValue: %.1f", x, y, res.val)

        self.debugf("SLEEP 1s")
        time.sleep(1)
        self._click(x, y)

    def debugf(self, message, *args):
        if self._debug:
            logger.info(message, *args)


def main():
    import uiautomator2 as u2
    d = u2.connect("bf755cab")
    # d.session("com.")
    s = d.session()

    t = CVToolKit()
    t._screenshot = s.screenshot
    t._click = s.click

    # t.click("@与微信好友玩")
    # t.click("开始游戏.jpg")
    t.click("单机.jpg")
    t.click("返回.jpg")
    # t.click("http://localhost:7000/static/继续.jpg")
    # t.click("http://localhost:7000/static/确定.jpg")
    # t.click("email.jpg")


if __name__ == "__main__":
    main()
