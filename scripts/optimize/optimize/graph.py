import matplotlib.pyplot as plt
import pandas as pd
import re
import math
# ----- Matplotlib の rc 設定 ----
config = {
    "font.size":20,
    "axes.xmargin" : 0,
    # "axes.grid":True,
    "axes.linewidth": 3,
    # "grid.linewidth": 3,
    "figure.figsize":[10.0, 7.0],
    "legend.fontsize": 18,
    "lines.linewidth": 3,
    "xtick.direction" : "in",
    "ytick.direction" : "in",
    "xtick.major.pad" : 10,
    "ytick.major.pad" : 10,
    "xtick.major.size" : 7,
    "ytick.major.size" : 7,
    "xtick.major.width" : 3,
    "ytick.major.width" : 3,
    "axes.unicode_minus": False
}
plt.rcParams.update(config)
# よくわからないがこれで Times New Roman が使える
plt.rcParams['font.family'] = 'DeJavu Serif'
plt.rcParams['font.serif'] = ['Times New Roman']

def phase_plot(df : pd.DataFrame):
    df.index = df.index * 10**12
    df.plot()
    max_y = df.max().max()
    val = 0
    y_list = []
    y_list_str = []
    while (val-2)*math.pi < max_y:
        y_list.append(val*math.pi)
        y_list_str.append(str(val)+"π")
        val += 2

    plt.yticks(y_list, y_list_str)
    plt.tick_params(labelsize=28)
    plt.xlabel("Time [ps]", size=32)  # x軸指定
    plt.ylabel("Phase difference [rad]", size=32)    # y軸指定
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

def voltage_plot(df : pd.DataFrame):
    df.plot()
    plt.tick_params(labelsize=28)
    plt.xlabel("Time [ps]", size=24)  # x軸指定
    plt.ylabel("Voltage [V]", size=24)    # y軸指定
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

def current_plot(df : pd.DataFrame):
    df.plot()
    plt.tick_params(labelsize=28)
    plt.xlabel("Time [ps]", size=24)  # x軸指定
    plt.ylabel("Current [A]", size=24)    # y軸指定
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

def sim_plot(df : pd.DataFrame):
    l = df.columns
    phase_list = list(filter(lambda s: re.search('P\(.+\)',s, flags=re.IGNORECASE), l))
    if not phase_list == []:
        phase_plot(df.filter(items=phase_list))    

    voltage_list = list(filter(lambda s: re.search('V\(.+\)',s, flags=re.IGNORECASE), l))
    if not voltage_list == []:
        voltage_plot(df.filter(items=voltage_list))
        
    current_list = list(filter(lambda s: re.search('I\(.+\)',s, flags=re.IGNORECASE), l))
    if not current_list == []:
        current_plot(df.filter(items=current_list))


def margin_plot(margins : pd.DataFrame, filename = None):
    # バーのcolor
    plot_color = '#01b8aa'

    df = margins.sort_index()
    index = df.index
    column0 = df['low(%)']
    column1 = df['high(%)']

    # --- biasのカラーを変更したリスト ---
    index_color = []
    for i in index:
        if re.search('bias|Vb',i,flags=re.IGNORECASE):
            index_color.append('red')
        else:
            index_color.append(plot_color)
    # ------

    # 図のサイズ　sharey:グラフの軸の共有(y軸)
    fig, axes = plt.subplots(figsize=(10, len(index)/2.5), ncols=2, sharey=True)
    plt.subplots_adjust(wspace=0)
    fig.suptitle("Margins", y=1.1)
    axes[0].set_ylabel("Elements", fontsize=20)
    axes[1].set_xlabel("%", fontsize=20)

    # 分割した 0 グラフ
    axes[0].barh(index, column0, align='center', color=index_color)
    axes[0].set_xlim(-100, 0)
    # axes[0].grid(axis='y')


    # 分割した 1 グラフ
    axes[1].barh(index, column1, align='center', color=index_color)
    axes[1].set_xlim(0, 100)
    axes[1].tick_params(axis='y', colors=plot_color)  # 1 グラフのメモリ軸の色をプロットの色と合わせて見れなくする
    # axes[1].grid(axis='y')


    if filename != None:
        fig.savefig(filename)
        plt.close(fig)