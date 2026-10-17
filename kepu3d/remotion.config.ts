import {Config} from '@remotion/cli/config';

Config.setChromiumOpenGlRenderer('swangle');
Config.setVideoImageFormat('jpeg');
Config.setPixelFormat('yuv420p');
Config.setCodec('h264');
Config.setCrf(18);
