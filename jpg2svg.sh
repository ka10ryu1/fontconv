#!/bin/bash

# 実行時に指定された引数の数、つまり変数 $# の値が 3 でなければエラー終了。
if [ $# -ne 1 ]; then
  echo "指定された引数は$#個です。" 1>&2
  echo "実行するには1個の入力ファイル名パスが必要です。" 1>&2
  echo "例）$ ./jpg2svg result/predict.jpg"
  exit 1
fi

# fpath: 入力ファイル名
fpath=$1
# fpath_bmp: 入力ファイル名の拡張子をbmpに変換したファイル名
fpath_bmp="${fpath%.*}.bmp"
# 入力ファイルを200%のbmp形式に変換する
echo "convert" $fpath "->" $fpath_bmp "(200%)"
convert $fpath -resize 200% $fpath_bmp
# 200%のbmp形式のファイルをsvg形式に変換する
echo "potrace" $fpath_bmp
potrace -s $fpath_bmp -k0.75 -a 1.3
# bmp形式は不要なので削除
echo "rm" $fpath_bmp
rm -rf $fpath_bmp

exit 0
