Title: Git中一些容易被忽视的东西
Category: git
Tags: git
Date: 2016-03-27 03:37:03
Modified: 2016-04-07 18:58:16
Authors: importcjj

#### 1. 修改commit的message
1. 修改最近一次commit的message  `git commit --amend` 然后输入想要修改的message
2. 批量修改commit的message `git rebase -i HEAD~n` n为一个数字，表示最近n次commit, 将想要修改的commit id前的pick改成reword(r)命令, 然后修改id后的commit message,  保存退出后即可.

#### 2. 合并连续的多个commit为一个commit
使用`git rebase -i HEAD~n` 把将被合并的commit id前的pick命令改成squash(s)

#### 3. 忽略已被提交过的文件

1. `git rm --cached <filename>` 不用担心，这一步只是删除该文件在版本库中的追踪，并不会正真删除磁盘上的物理文件
2. 更新.gitignore文件, 如果之前已经更新过了，就可以直接跳过这一步了。
3. add + commit 提交

#### 4. 新建一个orphan(孤儿)分支

`git checkout --orphan <name>`

#### 4. git diff 查看修改内容
这里要说的是两种情况:
1. 文件改动还未加入暂存区（即未git add），这种情况直接使用`git diff`或者`git diff <path`查看一个或多个文件的改动情况。
2. 文件改动已经加入暂存区，这种情况需要使用参数**--staged**, 即`git diff --staged`或者`git diff --staged <path>`来查看暂存区中的文件与代码仓库中的文件差异。
注： 可以使用**difftool**来代替**diff**命令从而更加清晰的查看文件改动！
