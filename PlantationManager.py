import cv2
import numpy as np

PZ_count = 0
PZ = [[(319, 276), (338, 276), (447, 276), (546, 276)]
    , [(98, 256), (145, 256), (130, 221), (180, 221)]
    , [(267, 193), (307, 196), (306, 180), (347, 194)]
    , [(522, 203), (552, 203), (587, 205), (612, 213)]]

table = {
    "RedSquare": "rosesred.png",
    "RedCircle": "gerber.png",
    "RedTriangle ": "poinsettia.png",
    "BlueSquare": "orchid.png",
    "BlueCircle": "tulipBlue.png",
    "BlueTriangle": "lilac.png",
    "GreenSquare": "hibiscusyellow.png",
    "GreenCircle": "lily.png",
    "GreenTriangle": "marigold.png"
}
window = 'Plantation'


def blend_transparent(face_img, overlay_t_img):
    overlay_img = overlay_t_img[:, :, :3]  # Grab the BRG planes
    overlay_mask = overlay_t_img[:, :, 3:]  # And the alpha plane
    background_mask = 255 - overlay_mask
    overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
    background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)
    face_part = (face_img * (1 / 255.0)) * (background_mask * (1 / 255.0))
    overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))
    return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))


def update_view(shape, color, count):
    global PZ_count
    plant_loc = table[color + shape]
    plant = cv2.imread('Resources/Seedlings/' + plant_loc, -1)
    plant = cv2.resize(plant, (70, 70), interpolation=cv2.INTER_AREA)
    for i in range(min(4, count)):
        x, y = PZ[PZ_count][i]
        plantation[y - 70:y, x - 35:x + 35] = blend_transparent(plantation[y - 70:y, x - 35:x + 35], plant)
    PZ_count += 1
    cv2.imshow(window, plantation)


def attach():
    global plantation
    plantation = cv2.imread('Resources/Plantation.png')
    cv2.imshow(window, plantation)
    cv2.waitKey(1)


def detach():
    global plantation
    cv2.imwrite('ResultantPlantation.jpeg', plantation)
    cv2.destroyWindow(window)
    cv2.destroyAllWindows()
