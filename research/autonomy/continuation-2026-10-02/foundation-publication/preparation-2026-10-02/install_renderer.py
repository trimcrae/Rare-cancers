from guarded_process import run
run(['sudo','apt-get','update','-qq'],'/tmp/install-update.log',180)
run(['sudo','apt-get','install','--no-install-recommends','-y','libreoffice-writer','poppler-utils','fonts-liberation'],'/tmp/install-renderer.log',360)
run(['python3','-m','pip','install','--no-cache-dir','pdf2image','Pillow','pypdf'],'/tmp/install-python.log',120)
