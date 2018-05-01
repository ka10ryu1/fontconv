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

以下を実行する。

```console
$ ./create_dataset.py Font/00_yu_gothic_12pt.png Font/01_Berlin_Sans_FB_12pt.png
```

`result`フォルダが作成され、以下のデータが保存されていることを確認する

- `dataset.json`
- `test_128x128_000100.npz`
- `train_128x128_000900.npz`

`dataset.json`は作成されたデータの情報が格納されている。

```console
$ cat result/dataset.json
{
    "conv_font": "Font/01_Berlin_Sans_FB_12pt.png",
    "font_num": 10,
    "font_size": 64,
    "img_num": 1000,
    "img_size": 128,
    "out_path": "./result/",
    "pre_font": "Font/00_yu_gothic_12pt.png",
    "round": 1000,
    "train_per_all": 0.9
}
```

`test_128x128_000100.npz`と`train_128x128_000900.npz`は学習に使用するテストデータと学習データ。それぞれの中身を確認するには以下を入力する。

```console
$ Tools/npz2jpg.py result/test_128x128_000100.npz
```

表示された画像の上段が入力画像（`yu_gothic`）で、下段が正解画像（作成したいフォント）。その他`Tools`の機能を利用したい場合は`Tools/README.md`を参照されたい。


## 2. 学習する

以下を実行する

```console
$ ./train.py
```

`result`フォルダに以下のデータが保存されていることを確認する

- `*_train.json`
- `*.log`
- `*.model`
- `*_10.snapshot`
- `*_graph.dot`
- `loss.png`

## 3. 学習で作成されたモデルを使用する

```console
$ ./predict.py result/*.model result/*_train.json Font/test.png
```

その他のパラメータ設定は`-h`で確認する。デモと同様のパラメータにしたい場合は`Model/param.json`を参考にすると良い。
