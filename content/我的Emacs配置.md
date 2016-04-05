Title: 我的Emacs的配置
Category: Emacs
Tags: Emacs
Date: 2016-04-05 19:41:06
Author: importcjj


#### 记录Emacs的配置和相关配置，以备万一。 ~/.emacs/init.el

```elisp

;;; package --- Emacs Configure
;;; Commentary:
;;; code:
(require 'package)
(add-to-list 'package-archives '("melpa" . "http://melpa.org/packages/"))

(package-initialize)
(when (not package-archive-contents)
  (package-refresh-contents))

(when (memq window-system '(mac ns))
  (exec-path-from-shell-initialize))

;; add maunal/ and top dir to load-path
(let ((base "~/.emacs.d/maunal"))
  (add-to-list 'load-path base)
  (dolist (f (directory-files base))
    (let ((name (concat base "/" f)))
      (when (and (file-directory-p name)
                 (not (equal f ".."))
                 (not (equal f ".")))
        (add-to-list 'load-path name)))))


;; BASIC CONFIGURE
;; mouse intergration
(xterm-mouse-mode t)
(global-set-key [mouse-4] '(lambda ()
                             (interactive)
                             (scroll-down 1)))
(global-set-key [mouse-5] '(lambda ()
                             (interactive)
                             (scroll-up 1)))
;; font
;;(set-frame-font "Consolas-16")
(set-face-attribute 'default nil :family "Consolas")
(set-face-attribute 'default nil :height 200)
;; (load-theme 'noctilux t)
(setq-default kill-whole-line t)
(setq require-final-newline t)
(global-linum-mode t)
(setq linum-format "%3d ")
(electric-pair-mode 1)
(fset 'yes-or-no-p 'y-or-n-p)
(global-set-key (kbd "M-q") 'other-window)

;;(load-file "~/.emacs.d/maunal/emacs-for-python/epy-init.el")

;;(add-hook 'python-mode-hook (lambda() (electric-indent-mode -1)))

 ;; Standard Jedi.el setting
(require 'jedi)
(add-hook 'python-mode-hook 'jedi:setup)
(setq jedi:complete-on-dot t)

;; flymake-python-pyflakes
;;(require 'flymake-python-pyflakes)
(require 'flycheck)
(add-hook 'after-init-hook 'global-flycheck-mode)

;; auto pep8 on save
(require 'py-autopep8)
(add-hook 'python-mode-hook 'py-autopep8-enable-on-save)
(setq py-autopep8-options '("--max-line-length=100"))

;; move line and region
(require 'move-lines)
(move-lines-binding)

;;(require 'yaml-mode)
;;(add-to-list 'auto-mode-alist '("\\.yml$" . yaml-mode))
;;(add-to-list 'auto-mode-alist '("\\.sls\\'" . yaml-mode))

;; qucik insert new line
(require 'open-next-line)
;;
;; ace jump mode major function
;;
(autoload
  'ace-jump-mode
  "ace-jump-mode"
  "Emacs quick move minor mode"
  t)
;; you can select the key you prefer to
(define-key global-map (kbd "C-c h") 'ace-jump-mode)
;;
;; enable a more powerful jump back function from ace jump mode
;;
(autoload
  'ace-jump-mode-pop-mark
  "ace-jump-mode"
  "Ace jump back:-)"
  t)
(eval-after-load "ace-jump-mode"
  '(ace-jump-mode-enable-mark-sync))
(define-key global-map (kbd "C-c SPC") 'ace-jump-mode-pop-mark)
;; smex
(require 'smex) ; Not needed if you use package.el
(smex-initialize) ; Can be omitted. This might cause a (minimal) delay
                                        ; when Smex is auto-initialized on its first run.
(global-set-key (kbd "M-x") 'smex)
(global-set-key (kbd "M-X") 'smex-major-mode-commands)
;; This is your old M-x.
(global-set-key (kbd "C-c C-c M-x") 'execute-extended-command)

(require 'sr-speedbar)
(setq sr-speedbar-right-side nil)
(setq sr-speedbar-width 25)
(setq dframe-update-speed t)
(global-set-key (kbd "<f5>") (lambda()
                               (interactive)
                               (sr-speedbar-toggle)))

(defun go-mode-setup ()
  "Prepare for go mode."
  (setq compile-command "go build -v && go test -v && go vet")
  (define-key (current-local-map) "\C-c\C-c" 'compile)
  (go-eldoc-setup)
  (add-hook 'before-save-hook 'gofmt-before-save))
(add-hook 'go-mode-hook 'go-mode-setup)

(require 'go-autocomplete)
(require 'auto-complete-config)
(ac-config-default)

;;; init.el ends here
```

#### 相关插件

- jedi : python代码的静态分析工具
- pycheck : python代码规范检查工具
- py-autopep8 : python代码自动格式化工具
- yaml-mode : yaml文件编辑模式
- sr-speedbar : 侧边栏， F5开启/关闭
- ace-jump-mode : 代码首字母跳转工具
- color-theme-github : github的代码主题
- emacs-for-python : emacs开发python的相关有用套件
- go-autocomplete : galang的自动补全工具
- mouse
- move-lines : 代码行和快的快速移动工具
- open-next-line : 快速在当前行的上方或下方新建空白行
- smooth-scroll : 平缓滚动
