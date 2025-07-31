import cv2
video_path = 'benkyou11.mp4'
cap = cv2.VideoCapture(video_path)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

def rot_minus2(img):
    # 画像を-2度回転
    h,w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -2, 1.0)
    return cv2.warpAffine(img, M, (w, h))

def rot_2(img):
    # 画像を2度回転
    h,w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, 2, 1.0)
    return cv2.warpAffine(img, M, (w, h))

def thumb():
    for i in range(20):
        cap.set(cv2.CAP_PROP_POS_FRAMES, (i * frame_count / 20)+1)

        _, img = cap.read()
        width = img.shape[1]
        height = img.shape[0]

        # リサイズ
        img = cv2.resize(img, (width, height))
        outputPath = 'test_data/thumb_%02d.jpg'
        # 画像ファイルで書き出す
        # ファイル名には連番を付ける
        cv2.imwrite(outputPath % (i+160), img)
        
        if i % 2 == 0:
             #画像を-2度回転
            _,img = cap.read()
            img = rot_minus2(img)
            outputPath = 'images/thumb_rot%02d.jpg'
            cv2.imwrite(outputPath % (i+150), img)
            # 画像を2度回転
            _,img = cap.read()
            img = cv2.resize(img, (width, height))
            img = rot_2(img)
            outputPath = 'images/thumb_rot2%02d.jpg'
            cv2.imwrite(outputPath % (i+150), img)
    cap.release()



thumb()
