from __future__ import absolute_import
import collections
import threading
import queue
import time
import numpy as np

from .logger import logger
from . import names
from .orc cimport EventContext, Instrument
from . cimport q
from . import q
from pippi.soundbuffer cimport SoundBuffer

from cython.parallel import parallel, prange
from libc.stdlib cimport malloc, calloc, free

cdef void play_sequence(q.BufQ* buf_q, object event_q, object player, EventContext ctx, tuple onsets):
    """ Play a sequence of overlapping oneshots
    """
    cdef double delay_time = 0
    cdef object snd 
    cdef long elapsed = 0
    cdef object delay = threading.Event()
    cdef Py_ssize_t numonsets = len(onsets)
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t j = 0
    cdef Py_ssize_t k = 0
    cdef Py_ssize_t length = 0
    cdef double onset = 0
    cdef q.N* playbuf
    cdef int channels = 2
    cdef int samplerate = 44100
    cdef double start_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
    cdef double[:] _onsets = np.array(onsets, 'd')

    # FIXME onsets should be a python generator too
    for onset in onsets:
        generator = player(ctx)
        onset = _onsets[i]

        delay(onset)
        try:
            for snd in generator:
                playbuf = q.bufnode_init(snd, start_time + onset)
                q.bufq_push(buf_q, playbuf)

        except Exception as e:
            logger.error('Error during %s generator render: %s' % (ctx.instrument_name, e))

        #elapsed = time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - start_time

cdef void init_voice(object instrument, object params, q.BufQ* buf_q, object event_q):
    cdef EventContext ctx = instrument.create_ctx(params)
    ctx.running.set()

    loop = False
    if hasattr(instrument.renderer, 'loop'):
        loop = instrument.renderer.loop

    if hasattr(instrument.renderer, 'before'):
        # blocking before callback makes
        # its results available to voices
        ctx.before = instrument.renderer.before(ctx)

    # find all play methods
    players = set()

    cdef tuple onset_list = (0,)

    # The simplest case is a single play method 
    # with an optional onset list or callback
    if hasattr(instrument.renderer, 'play'):
        onsets = getattr(instrument.renderer, 'onsets', (0,))
        players.add((instrument.renderer.play, onsets))

    # Play methods can also be registered via 
    # an @player.init decorator, which also registers 
    # an optional onset list or callback
    if hasattr(instrument.renderer, 'player') \
        and hasattr(instrument.renderer.player, 'players') \
        and isinstance(instrument.renderer.player.players, set):
        players |= instrument.renderer.player.players

    cdef int count = 0

    while True:
        for player, onsets in players:
            try:
                ctx.count = count
                onset_list = (0,)
                try:
                    onset_list = tuple(onsets)
                except TypeError:
                    if callable(onsets):
                        onset_list = tuple(onsets(ctx))
                
                play_sequence(buf_q, event_q, player, ctx, onset_list)
            except Exception as e:
                logger.error('error calling play_sequence: %s' % e)
           
        count += 1

        if not loop or ctx.stop_all.is_set():
            break

    ctx.running.clear()

    if hasattr(instrument.renderer, 'done'):
        # When the loop has completed or playback has stopped, 
        # execute the done callback
        instrument.renderer.done(ctx)

