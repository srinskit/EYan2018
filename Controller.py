# import matplotlib.pyplot as plt

kp = .12
ki = 0.001
kd = 0.2
acc_err, prev_err, diff_err = 0, 0, 0
err_list = []
acc_list = []
diff_list = []

call_count = 0
record_vars = False
live_vars = False
debug_vars = False


def setup_live_plot():
    global live_vars
    live_vars = True
    # plt.ion()
    # plt.subplot(311)
    # plt.xlim([0, 1000])
    # plt.ylim([-200, 200])
    # plt.subplot(312)
    # plt.xlim([0, 1000])
    # plt.ylim([-5000, 5000])
    # plt.subplot(313)
    # plt.xlim([0, 1000])
    # plt.ylim([-50, 50])


def follow_line(err, fc):
    global acc_err, prev_err, diff_err, call_count, f
    call_count += 1
    acc_err += err
    diff_err = err - prev_err
    prev_err = err
    if live_vars:
        plot_vars_live()
    if record_vars:
        err_list.append(err)
        acc_list.append(acc_err)
        diff_list.append(diff_err)
    v_new_left = 20 - err * kp - acc_err * ki - diff_err * kd
    v_new_right = 15 + err * kp + acc_err * ki + diff_err * kd
    v_new_left = max(min(v_new_left, 100), -100)
    v_new_right = max(min(v_new_right, 100), -100)
    if debug_vars:
        f.write('%d %f %f %f %f %f\n' % (fc, err, acc_err, diff_err, v_new_left, v_new_right))
    return v_new_left, v_new_right


def reset():
    global acc_err, prev_err, diff_err
    acc_err, prev_err, diff_err = 0, 0, 0


def attach():
    global f
    if debug_vars:
        f = open('vars.txt', 'w')


def detach():
    global f
    if debug_vars:
        f.close()


def plot_vars():
    # if record_vars:
    #     x = range(len(err_list))
    #     plt.subplot(311)
    #     plt.plot(x, [0] * len(x))
    #     plt.plot(x, err_list)
    #     plt.subplot(312)
    #     plt.plot(x, [0] * len(x))
    #     plt.plot(x, acc_list)
    #     plt.subplot(313)
    #     plt.plot(x, [0] * len(x))
    #     plt.plot(x, diff_list)
    #     plt.show()
    pass


def plot_vars_live():
    # plt.subplot(311)
    # plt.scatter(call_count, prev_err, s=2, c='b')
    # plt.subplot(312)
    # plt.scatter(call_count, acc_err, s=2, c='b')
    # plt.subplot(313)
    # plt.scatter(call_count, diff_err, s=2, c='b')
    # plt.pause(1e-6)
    pass
