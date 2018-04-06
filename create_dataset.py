#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = '画像を読み込んでデータセットを作成する'
#

import os
import cv2
import argparse
import numpy as np

import Tools.imgfunc as IMG
import Tools.func as F


def command():
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('pre_font',   help='使用する入力フォント画像')
    parser.add_argument('conv_font',   help='使用する正解フォント画像')
    parser.add_argument('-fs', '--font_size', type=int, default=64,
                        help='挿入する画像サイズ [default: 64 pixel]')
    parser.add_argument('-is', '--img_size', type=int, default=128,
                        help='生成される画像サイズ [default: 128 pixel]')
    parser.add_argument('-fn', '--font_num', type=int, default=10,
                        help='フォント数 [default: 10]')
    parser.add_argument('-in', '--img_num', type=int, default=1000,
                        help='画像生成数 [default: 1000]')
    parser.add_argument('-r', '--round', type=int, default=1000,
                        help='切り捨てる数 [default: 1000]')
    parser.add_argument('-t', '--train_per_all', type=float, default=0.9,
                        help='画像数に対する学習用画像の割合 [default: 0.9]')
    parser.add_argument('-o', '--out_path', default='./result/',
                        help='データセット保存先 (default: ./result/)')
    return parser.parse_args()


def saveNPZ(x, y, name, folder, size):
    """
    入力データと正解データをNPZ形式で保存する
    [in] x:      保存する入力データ
    [in] y:      保存する正解データ
    [in] name:   保存する名前
    [in] folder: 保存するフォルダ
    [in] size:   データ（正方形画像）のサイズ
    """

    size_str = '_' + str(size).zfill(2) + 'x' + str(size).zfill(2)
    num_str = '_' + str(x.shape[0]).zfill(6)
    np.savez(F.getFilePath(folder, name + size_str + num_str), x=x, y=y)


def create(pre_font, conv_font, font_size, img_size, font_num, img_num):
    x = []
    y = []

    for i in range(img_num):
        img_len = np.min([pre_font.shape[0], conv_font.shape[0]])-1
        label = range(img_len)
        pre_img = IMG.blank((img_size, img_size, 3), 255)
        conv_img = IMG.blank((img_size, img_size, 3), 255)
        for j in range(font_num):
            num = np.random.choice(label, 1, replace=False)[0]
            pf = pre_font[num][1:, 1:, ]
            cf = conv_font[num][1:, 1:, ]
            pre_img, param = IMG.paste(pf, pre_img,
                                       mask_flg=False, rand_rot_flg=False)
            r, _x, _y = param
            conv_img, _ = IMG.paste(cf, conv_img, x=_x, y=_y,
                                    mask_flg=False, rand_pos_flg=False, rand_rot_flg=False)

        x.append(pre_img)
        y.append(conv_img)

    return np.array(x), np.array(y)


def imread(path, ch):
    if IMG.isImgPath(path):
        print('imread:\t', path)
        x = cv2.imread(path, IMG.getCh(ch))
    else:
        print('[ERROR] color image not found:', path)
        exit()

    return x


def main(args):

    # フォント画像の読み込み
    x = imread(args.pre_font, 3)
    y = imread(args.conv_font, 3)

    # フォント画像をフォントごとに分割する
    h, w = x.shape[:2]
    x, _ = IMG.splitSQ(x, h//3)
    y, _ = IMG.splitSQ(y, h//3)

    print('create images...')
    x, y = create(x, y, args.font_size, args.img_size, args.font_num, args.img_num)

    # 画像の並び順をシャッフルするための配列を作成する
    # compとrawの対応を崩さないようにシャッフルしなければならない
    # また、train_sizeで端数を切り捨てる
    # データをint8からfloat16に変えるとデータ数が大きくなるので注意
    print('shuffle images...')
    dtype = np.float16
    shuffle = np.random.permutation(range(len(x)))
    train_size = int(len(x) * args.train_per_all)
    train_x = IMG.imgs2arr(x[shuffle[:train_size]], dtype=dtype)
    train_y = IMG.imgs2arr(y[shuffle[:train_size]], dtype=dtype)
    test_x = IMG.imgs2arr(x[shuffle[train_size:]], dtype=dtype)
    test_y = IMG.imgs2arr(y[shuffle[train_size:]], dtype=dtype)
    print('train x/y:{0}/{1}'.format(train_x.shape, train_y.shape))
    print('test  x/y:{0}/{1}'.format(test_x.shape, test_y.shape))

    # 生成したデータをnpz形式でデータセットとして保存する
    # ここで作成したデータの中身を確認する場合はnpz2jpg.pyを使用するとよい
    print('save npz...')
    saveNPZ(train_x, train_y, 'train', args.out_path, args.img_size)
    saveNPZ(test_x, test_y, 'test', args.out_path, args.img_size)


if __name__ == '__main__':
    args = command()
    F.argsPrint(args)
    main(args)
