import Bot
import Controller
import Visionary as CompVision
from time import time as clock, sleep
import PlantationManager as Pm
import cv2


def main():
    Pm.attach()

    # Bot.soft_run = True
    Bot.attach()
    CompVision.global_threshold = True
    CompVision.debug_display = True
    state = CompVision.State
    CompVision.attach()

    Controller.debug_vars = True
    Controller.attach()
    call_count, zi_cooldown = 0, 20

    prev_state = state.NORM
    try:
        while True:
            print '----'
            prev_time = clock()
            view = Bot.get_view()
            print 'ft %f' % (clock() - prev_time)
            bot_state, val, uerr, fc = CompVision.process(view)
            print fc, val,
            if bot_state == state.NORM:
                print 'NORM'
                if prev_state == state.TURN:
                    print 'ALIGN'
                    if -10 <= val <= 10:
                        pass
                    else:
                        Bot.move(*((22, -22) if val < -10 else (-22, 22)))
                        bot_state = state.TURN
                else:
                    Bot.move(*Controller.follow_line(val, fc))
            elif bot_state == state.SHED:
                print 'SHED'
                if uerr is None:
                    Bot.move(0, 0)
                    break
                else:
                    Bot.move(*Controller.follow_line(val, fc))
            elif bot_state == state.TURN:
                print 'TURN'
                Controller.reset()
                if val == 'left':
                    Bot.move(-22, 22)
                if val == 'right':
                    Bot.move(22, -22)
            elif bot_state == state.ZI:
                print 'ZI'
                if call_count == 0:
                    Bot.move(0, 0)
                    # val = -420
                    # while val < -10 or val > 10:
                    #    bot_state, val, _, _ = CompVision.process(Bot.get_view())
                    #    Bot.move(*((20, -20) if val < -10 else (-20, 20)))
                    # Bot.move(0, 0)
                    good_view = Bot.get_good_view()
                    shape, color, count = CompVision.process_markers(good_view)
                    print good_view.shape
                    if shape is None or color is None or count is None:
                        print 'False ZI'
                    else:
                        print shape, color, count
                        Pm.update_view(shape, color, count)
                        Bot.blink(color, count)
                    call_count += 1
                    Bot.move(*Controller.follow_line(val, fc))
                else:
                    Bot.move(*Controller.follow_line(val, fc))
            elif bot_state == state.NO_LINE:
                print 'NOLINE'
            else:
                print 'QUIT'
                Bot.move(0, 0)
                break
            prev_state = bot_state
            if 0 < call_count < zi_cooldown:
                call_count += 1
            else:
                call_count = 0
            print 'tt %f' % (clock() - prev_time)
    except KeyboardInterrupt:
        print 'KeyInt'

    # Controller.plot_vars()
    Controller.detach()

    CompVision.detach()
    Bot.detach()
    Pm.detach()


if __name__ == '__main__':
    main()
