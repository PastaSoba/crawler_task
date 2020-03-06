# coding:utf-8
import sys
import pathlib
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')

if __name__ == "__main__":
    args = sys.argv

    if len(args) == 1:
        print("引数をセットしてください\n（例：python interntask.py projectname）", file=sys.stderr)
    else:
        projectname = args[1]
        filename = args[1] + ".py"
        filepath = str(current_dir) + '/today/' + args[1] + ".py"

        with open(filepath, mode='x', encoding='utf_8') as newfile:
            with open("template.py", "r", encoding='utf_8') as readfile:
                for line in readfile:
                    print(line.replace("TEMPLATE", projectname),
                          file=newfile, end="")
