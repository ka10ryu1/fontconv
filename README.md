# 概要

英語にしか対応していないフォントで日本語も（ムリヤリ）対応させる

## 学習結果

## デモを実行する



#  動作環境

- **Ubuntu** 16.04.4 LTS ($ cat /etc/issue)
- **Python** 3.5.2 ($ python3 -V)
- **chainer** 4.0.0 ($ pip3 show chainer | grep Ver)
- **numpy** 1.14.2 ($ pip3 show numpy | grep Ver)
- **cupy** 4.0.0 ($ pip3 show cupy | grep Ver)
- **opencv-python** 3.4.0.12 ($ pip3 show opencv-python | grep Ver)

# ファイル構成

## 生成方法

```console
$ ls `find ./ -maxdepth 3 -type f -print` | xargs grep 'help = ' --include=*.py >& log.txt
$ tree >& log.txt
```

```console
.
├── Font > データセット（テスト用含む）
├── LICENSE
├── Lib
│   ├── network.py > fontconvのネットワーク部分
│   └── plot_report_log.py
├── Model
│   ├── demo.model
│   └── param.json
├── README.md
├── Tools
│   ├── LICENSE
│   ├── README.md
│   ├── Tests
│   │   ├── Lenna.bmp       > テスト用画像
│   │   ├── Mandrill.bmp    > テスト用画像
│   │   ├── test_getfunc.py > getfuncのテスト用コード
│   │   └── test_imgfunc.py > imgfuncのテスト用コード
│   ├── concat.py          > 複数の画像を任意の行列で結合する
│   ├── dot2png.py         > dot言語で記述されたファイルをPNG形式に変換する
│   ├── func.py            > 便利機能
│   ├── getfunc.py         > 各種パラメータ取得に関する便利機能
│   ├── imgfunc.py         > 画像処理に関する便利機能
│   ├── npz2jpg.py         > 作成したデータセット（.npz）の中身を画像として出力する
│   ├── plot_diff.py       > logファイルの複数比較
│   └── png_monitoring.py  > 任意のフォルダの監視
├── auto_train.sh
├── clean_all.sh
├── create_dataset.py > 画像を読み込んでデータセットを作成する
├── predict.py        > モデルとモデルパラメータを利用して推論実行する
├── pruning.py        > モデルの枝刈をする
└── train.py          > 学習メイン部
```



# チュートリアル

## 1. データセットを作成する

```console
$ ./train.py -i FontData/
```


## 2. 学習する

### 実行

```console
$ ./train.py -i FontData/
```
