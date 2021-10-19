import os
import sys

# 引数で入力するのは　python optimizer.py simulation_file output_file
if __name__ == "__main__":
    if len(sys.argv) == 3:
        print('\033[31mcurrent dir:\t\t\033[0m', os.getcwd())
        print('\033[31mdir of this py program:\t\033[0m', os.path.dirname(__file__))
        if os.path.exists(sys.argv[1]):
            print("\033[31msimulation file:\033[0m\t",sys.argv[1])
        else:
            print("\033[31m[ERROR]\033[0m file not exist:\t",sys.argv[1])
            sys.exit()

        print("\033[31moutput file:\033[0m\t\t",sys.argv[2])
        if os.path.exists(sys.argv[2]):
            val = input('すでにファイルが存在しています。上書きしますか？[y/n]: ')
            if val == "y":
                print("上書き")
            else:
                print("他のファイルを入力してください。プログラムを終了します。")
                sys.exit()

    else:
        print("\033[31m[ERROR]\033[0m Wrong number of arguments for the function.")




    # os.mkdir(path)

