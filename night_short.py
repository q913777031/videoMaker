"""兼容入口：等价于 python3 -m kepu.build --topic night（其余参数原样传递）。"""

import sys

from kepu.build import main

if __name__ == "__main__":
    sys.argv[1:1] = ["--topic", "night"]
    main()
