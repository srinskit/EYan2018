import cv2
import numpy as np
import imutils

fourcc = cv2.VideoWriter_fourcc(*'XVID')
kernel = np.ones((5, 5), np.uint8)


class State:
    QUIT, NO_LINE, NORM, TURN, ZI, SHED = range(-2, 4)

    def __init__(self):
        pass


debug_display = False
global_threshold = False
off = 120
turn_off = .05
fourcc = cv2.VideoWriter_fourcc(*'XVID')
font = cv2.FONT_HERSHEY_SIMPLEX
frame_count = 0
thresh_count, stable_count = 0, 20


def process(gray):
    global frame_count, thresh, thresh_count, out
    cm, cd, fly, fry, err = None, None, None, None, 0
    pul, pdl, pur, pdr = None, None, None, None
    u, m, d = .15, .7, .9
    if gray is not None:
        frame_count += 1
        h, w = gray.shape
        gray = gray[100:h, 50:w - 50]
        h, w = gray.shape
        if thresh_count < stable_count or not global_threshold:
            thresh, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            thresh_count += 1
        _, bin_gray = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY_INV)
        bin_gray = cv2.erode(bin_gray, kernel, iterations=1)

        wu, plu, pru = path_on_line_horizontal(bin_gray, u)
        wm, plm, prm = path_on_line_horizontal(bin_gray, m)
        wd, pld, prd = path_on_line_horizontal(bin_gray, d)

        wtl, putl, pdtl = path_on_line_vertical(bin_gray, turn_off)
        wtr, putr, pdtr = path_on_line_vertical(bin_gray, 1 - turn_off)

        if wm > 0 and wd > 0:
            cm = (plm[0] + prm[0]) // 2
            cd = (pld[0] + prd[0]) // 2

            fly = lambda y: cm - off + (cd - cm) * (y - int(m * h)) / int((d - m) * h)
            fry = lambda y: cm + off + (cd - cm) * (y - int(m * h)) / int((d - m) * h)

            wl, pul, pdl = path_on_line(bin_gray, fly)
            wr, pur, pdr = path_on_line(bin_gray, fry)
        else:
            wl, pul, pdl = 0, None, None
            wr, pur, pdr = 0, None, None

        if wd > 0:
            err = -(pld[0] + prd[0]) / 2 + w / 2
        if wu > 0:
            uerr = -(plu[0] + pru[0]) / 2 + w / 2
        else:
            uerr = None
        if debug_display:
            mark(bin_gray, plu, pru, 100)
            mark(bin_gray, plm, prm, 100)
            mark(bin_gray, pld, prd, 100)
            mark(bin_gray, putl, pdtl, 100)
            mark(bin_gray, putr, pdtr, 100)
            if wm > 0 and wd > 0:
                cv2.line(bin_gray, (cm, int(m * h)), (cd, int(d * h)), 100, 2)
                tmp = int(turn_off * w)
                cv2.line(bin_gray, (tmp, 0), (tmp, h), 100, 2)
                cv2.line(bin_gray, (w - tmp, 0), (w - tmp, h), 100, 2)
                cv2.line(bin_gray, (fly(0), 0), (fly(h), h), 100, 2)
                cv2.line(bin_gray, (fry(0), 0), (fry(h), h), 100, 2)

                mark(bin_gray, pul, pdl, 100)
                mark(bin_gray, pur, pdr, 100)
            cv2.putText(bin_gray, str(frame_count), (0, 25), font, .8, 170, 2, cv2.LINE_AA)
            cv2.imshow('gray', bin_gray)
            out.write(cv2.cvtColor(bin_gray, cv2.COLOR_GRAY2BGR))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return State.QUIT, 0, uerr, frame_count

        if wtl > 0 and wtr > 0:
            return State.SHED, err, uerr, frame_count
        if wtl > 0 and wu <= 0:
            if putl[1] > h * .7:
                return State.TURN, 'left', uerr, frame_count
        if wtr > 0 and wu <= 0:
            if putr[1] > h * .7:
                return State.TURN, 'right', uerr, frame_count
        if wl > 0 and wr > 0:
            if pul[1] > h * .8 or pur[1] > h * .8:
                return State.ZI, err, uerr, frame_count

        if wd > 0:
            return State.NORM, err, uerr, frame_count
        else:
            return State.NO_LINE, None, uerr, frame_count
    return State.QUIT, 0, 0, frame_count


def path_on_line_horizontal(bin_gray, hp):
    h, w = bin_gray.shape
    line_y = int(hp * h)
    bin_line = bin_gray[line_y, :]
    xs, = np.nonzero(bin_line)
    if len(xs) > 0:
        return xs[-1] - xs[0], (xs[0], line_y), (xs[-1], line_y)
    return 0, None, None


def path_on_line_vertical(bin_gray, wp):
    h, w = bin_gray.shape
    line_x = int(wp * w)
    bin_line = bin_gray[:, line_x]
    ys, = np.nonzero(bin_line)
    if len(ys) > 0:
        return ys[-1] - ys[0], (line_x, ys[0]), (line_x, ys[-1])
    return 0, None, None


def path_on_line(bin_gray, fy):
    h, w = bin_gray.shape
    bin_line = np.zeros((h,))
    for y in range(0, h):
        if 0 <= fy(y) < w:
            bin_line[y] = bin_gray[y, fy(y)]
    ys, = np.nonzero(bin_line)
    if len(ys) > 0:
        return ys[-1] - ys[0], (fy(ys[0]), ys[0]), (fy(ys[-1]), ys[-1])
    return 0, None, None


def mark(frame, pt1, pt2, color):
    if debug_display and pt1 is not None and pt2 is not None:
        cv2.circle(frame, pt1, 4, color, 3)
        cv2.circle(frame, pt2, 4, color, 3)
        c = (pt1[0] + pt2[0]) / 2, (pt1[1] + pt2[1]) / 2
        cv2.circle(frame, c, 4, color, 3)


def cv2_plot(line, (h, w)):
    plot = np.zeros((h, w), np.uint8)
    i = 0
    for val in line:
        cv2.line(plot, (i, int(h * .5)), (i, int(h * .5) - val), 255, 1)
        i += 1
    return plot


def find_markers(roi):
    h, w, _ = roi.shape
    median_color = np.median(np.median(roi[w / 4:3 * w / 4, h / 4:2 * h / 4], axis=1), axis=0)
    colors = ['Blue', 'Green', 'Red']
    color_i = median_color.argmax()
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hsv[:, :, 0] = (hsv[:, :, 0] + 30) % 180
    min_area, max_area = 500, 15000
    s_low, s_high = 2 * 255 / 5, 255
    v_low, v_high = 255 / 5, 255
    h_low, h_high = [120, 60, 0], [180, 120, 60]
    mask = cv2.inRange(hsv, (h_low[color_i], s_low, v_low), (h_high[color_i], s_high, v_high))
    mask = cv2.erode(mask, np.ones((5, 5)), iterations=2)
    # mask = cv2.medianBlur(mask, 5)
    _, contours, _ = cv2.findContours(np.copy(mask), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    shape = None
    for contour in contours:
        if min_area < cv2.contourArea(contour) < max_area:
            poly_coord = cv2.approxPolyDP(contour, 0.03 * cv2.arcLength(contour, True), True)
            n_vertices = len(poly_coord)
            if n_vertices == 3:
                shape = 'Triangle'
            elif n_vertices == 4:
                shape = 'Square'
            else:
                shape = 'Circle'
    return colors[color_i], shape


def process_markers(img):
    hi, wi, _ = img.shape
    blur = cv2.medianBlur(img, 31)
    edge = imutils.auto_canny(blur)
    edge = cv2.dilate(edge, np.ones((5, 5)), iterations=2)
    _, contours, hierarchy = cv2.findContours(np.copy(edge), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img_tmp = np.copy(img)
    cv2.drawContours(img_tmp, contours, -1, (100, 0, 0), 2)
    cv2.drawContours(edge, contours, -1, 100, 2)
    cnt = 0
    roi_ptr = []
    padding = 10
    for i in range(len(hierarchy[0])):
        if hierarchy[0][i][3] == -1:
            x, y, w, h = cv2.boundingRect(contours[i])
            if 2500 < w * h < 5e4 and h < 200 and w < 200:
                roi_ptr.append(
                    (max(x - padding, 0), max(0, y - padding), min(w + 2 * padding, wi), min(hi, h + 2 * padding)))
                cnt += 1
                cv2.rectangle(img_tmp, (x - padding, y - padding), (x + w + padding, y + w + padding), (0, 0, 255), 2)
    # for x, y, w, h in roi_ptr:
    #     print find_markers(img[y:y + w, x:x + w])
    if len(roi_ptr) == 0:
        return None, None, None
    x, y, w, h = roi_ptr[0]
    color, shape = find_markers(img[y:y + w, x:x + w])
    return color, shape, len(roi_ptr)


def attach():
    global out
    if debug_display:
        out = cv2.VideoWriter('PB#NITK.avi', fourcc, 10, (540, 380))


def detach():
    global out
    if debug_display:
        cv2.waitKey(0)
        cv2.destroyWindow('ZI')
        cv2.destroyWindow('gray')
        out.release()
