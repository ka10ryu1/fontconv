#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = 'モデルとモデルパラメータを利用して推論実行する'
#

import logging
# basicConfig()は、 debug()やinfo()を最初に呼び出す"前"に呼び出すこと
level = logging.INFO
logging.basicConfig(format='%(message)s')
logging.getLogger('Tools').setLevel(level=level)

import cv2
import time
import argparse
import numpy as np

import chainer
import chainer.links as L
from chainer.cuda import to_cpu

from Lib.network import JC_DDUU as JC
import Tools.imgfunc as IMG
import Tools.getfunc as GET
import Tools.func as F


def command():
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('model',
                        help='使用する学習済みモデル')
    parser.add_argument('param',
                        help='使用するモデルパラメータ')
    parser.add_argument('jpeg', nargs='+',
                        help='使用する画像のパス')
    parser.add_argument('--batch', '-b', type=int, default=20,
                        help='ミニバッチサイズ [default: 20]')
    parser.add_argument('--gpu', '-g', type=int, default=-1,
                        help='GPU ID [default -1]')
    parser.add_argument('--out_path', '-o', default='./result/',
                        help='生成物の保存先[default: ./result/]')
    return parser.parse_args()


def encDecWrite(img, ch, quality, out_path='./result', val=-1):
    """
    画像の圧縮と保存を実行する
    [in] img:      圧縮したい画像
    [in] ch:       圧縮したい画像のチャンネル数
    [in] quality:  圧縮率（低いほど高圧縮）
    [in] out_path: 出力先フォルダ
    [in] val:      保存時の連番（負数で保存しない）
    [out] 圧縮済み画像
    """

    # 入力画像を圧縮して劣化させる
    comp = IMG.encodeDecode(img, IMG.getCh(ch), quality)
    # 比較のため圧縮画像を保存する
    if(val >= 0):
        path = F.getFilePath(out_path, 'comp-' +
                             str(val * 10).zfill(3), '.jpg')
        cv2.imwrite(path, comp)

    return comp


def predict(model, data, batch, org_shape, rate, gpu):
    """
    推論実行メイン部
    [in]  model:     推論実行に使用するモデル
    [in]  data:      分割（IMG.split）されたもの
    [in]  batch:     バッチサイズ
    [in]  org_shape: 分割前のshape
    [in]  rate:      出力画像の拡大率
    [in]  gpu:       GPU ID
    [out] img:       推論実行で得られた生成画像
    """

    # dataには圧縮画像と分割情報が含まれているので、分離する
    comp, size = data
    imgs = []
    st = time.time()
    # バッチサイズごとに学習済みモデルに入力して画像を生成する
    for i in range(0, len(comp), batch):
        x = IMG.imgs2arr(comp[i:i + batch], gpu=gpu)
        y = model.predictor(x)
        imgs.extend(IMG.arr2imgs(to_cpu(y.array)))

    print('exec time: {0:.2f}[s]'.format(time.time() - st))
    # 生成された画像を分割情報をもとに結合する
    buf = [np.vstack(imgs[i * size[0]: (i + 1) * size[0]])
           for i in range(size[1])]
    img = np.hstack(buf)
    # 出力画像は入力画像の2倍の大きさになっているので半分に縮小する
    img = IMG.resize(img, 1 / rate)
    # 結合しただけでは画像サイズがオリジナルと異なるので切り取る
    return img[:org_shape[0], :org_shape[1]]


def cleary(img, clip_limit=3, grid=(8, 8), thresh=225):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid)
    dst = clahe.apply(img)
    th = dst.copy()
    th[dst > thresh] = 255
    return th


def main(args):
    # jsonファイルから学習モデルのパラメータを取得する
    p = ['unit', 'shape', 'shuffle_rate', 'actfun1', 'actfun2']
    unit, shape, sr, af1, af2 = GET.jsonData(args.param, p)
    af1 = GET.actfun(af1)
    af2 = GET.actfun(af2)
    ch, size = shape[:2]
    # 学習モデルを生成する
    model = L.Classifier(
        JC(n_unit=unit, n_out=ch, rate=sr, actfun1=af1, actfun2=af2)
    )

    # load_npzのpath情報を取得し、学習済みモデルを読み込む
    load_path = F.checkModelType(args.model)
    try:
        chainer.serializers.load_npz(args.model, model, path=load_path)
    except:
        import traceback
        traceback.print_exc()
        print(F.fileFuncLine())
        exit()

    # GPUの設定
    if args.gpu >= 0:
        chainer.cuda.get_device_from_id(args.gpu).use()
        model.to_gpu()
    else:
        model.to_intel64()

    # 高圧縮画像の生成
    ch_flg = IMG.getCh(ch)
    org_imgs = [IMG.resize(cv2.imread(name, ch_flg), 2)
                for name in args.jpeg if IMG.isImgPath(name)]
    imgs = []
    # 学習モデルを入力画像ごとに実行する
    for i, img in enumerate(org_imgs):
        with chainer.using_config('train', False):
            dst = predict(
                model,
                IMG.splitSQ(img, size, w_rate=1.0),
                args.batch, img.shape, sr, args.gpu
            )

        # 生成結果を保存する
        name = F.getFilePath(args.out_path, 'predict_raw', '.jpg')
        cv2.imwrite(name, IMG.resize(dst, 0.5))
        dst = cleary(dst)
        name = F.getFilePath(args.out_path, 'predict', '.jpg')
        print('save:', name)
        cv2.imwrite(name, IMG.resize(dst, 0.5))
        imgs.append(dst)

    for i, j in zip(org_imgs, imgs):
        if (i.shape[0] + j.shape[0]) > i.shape[1]:
            img = IMG.resize(np.hstack([i, j]), 0.5)
        else:
            img = IMG.resize(np.vstack([i, j]), 0.5)

        cv2.imshow('view', img)
        cv2.waitKey()


if __name__ == '__main__':
    args = command()
    F.argsPrint(args)
    main(args)
