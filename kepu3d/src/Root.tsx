import React from 'react';
import {CalculateMetadataFunction, Composition, Still} from 'remotion';
import {Kepu} from './Kepu';
import {KepuProps} from './types';

const empty: KepuProps = {
  slug: 'demo', fps: 30, total: 2, width: 1080, height: 1920,
  layout: {name: 'vertical', text_size: 80, text_line_gap: 108, text_x: 505, text_y: 420, text_align: 'center',
    ref_size: 60, tag_size: 34, tag_x: 90, tag_y: 236},
  shots: [{no: 1, start: 0, dur: 2, lines: ['示例'], tag: '情境演绎', credit: false, cue: {}}],
  subshots: [{shot: 1, k: 0, start: 0, end: 2, why: ''}], hits: [], audio: '', cover: null,
};

const meta: CalculateMetadataFunction<KepuProps> = ({props}) => ({
  durationInFrames: Math.round(props.total * props.fps), fps: props.fps, width: props.width, height: props.height,
});

export const Root: React.FC = () => (
  <>
    <Composition id="Kepu" component={Kepu} durationInFrames={60} fps={30} width={1080} height={1920}
      defaultProps={empty} calculateMetadata={meta} />
    <Still id="Cover" component={Kepu} width={1080} height={1920} defaultProps={empty}
      calculateMetadata={({props}) => ({width: props.width, height: props.height})} />
  </>
);
