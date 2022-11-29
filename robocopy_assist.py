import os
import hashlib
import subprocess as sp
import datetime 

from tkinter import *
from tkinter import filedialog

def get_directory_path(entry_widget: Entry):
	dir=filedialog.askdirectory(parent=root)
	if len(dir)>0:
		entry_widget.delete(0, END)
		entry_widget.insert(0, dir)

def get_dic_hash(path: str):
	result=dict()
	for i in os.walk(path):
		root=i[0]
		dirnames=i[1]
		filenames=i[2]

		for filename in filenames:
			fullpath=os.path.join(root, filename)
			with open(fullpath, "rb") as fd:
				digest=hashlib.md5(fd.read()).hexdigest()
			result[fullpath]=digest
	return result

root=Tk()
root.title("Robocopy_assist")
root.geometry("840x600")

# Input settings
frame_path=LabelFrame(root, text="Path settings", padx=20, pady=20)
frame_path.pack(side="top", fill="both", expand=True, padx=5, pady=5)

## Source input
def get_src_path():	get_directory_path(entry_src)
label_src=Label(frame_path, text="Source : ").grid(row=0, column=0)
entry_src=Entry(frame_path)
entry_src.grid(row=0, column=1, ipadx=200)
btn_src=Button(frame_path, text="Find", command=get_src_path).grid(row=0, column=2)

## Destination input
def get_dest_path():	get_directory_path(entry_dest)
label_dest=Label(frame_path, text="Destination : ")
label_dest.grid(row=1, column=0)
entry_dest=Entry(frame_path)
entry_dest.grid(row=1, column=1, ipadx=200)
btn_dest=Button(frame_path, text="Find", command=get_dest_path).grid(row=1, column=2)

## Log path input
def get_log_path():	get_directory_path(entry_log)
label_log=Label(frame_path, text="Log : ")
label_log.grid(row=2, column=0)
entry_log=Entry(frame_path)
entry_log.grid(row=2, column=1, ipadx=200)
btn_log=Button(frame_path, text="Find", command=get_log_path).grid(row=2, column=2)

# Options
frame_options=LabelFrame(root, text="Options", padx=20, pady=20)
frame_options.pack(fill="both", expand=True, padx=5, pady=5)

## Check
def event_cb_log():
	value=cb_log_value.get()
	entry_log['state']=NORMAL if value else DISABLED

cb_log_value=BooleanVar()
cb_log=Checkbutton(frame_options, text="/Log", variable=cb_log_value, command=event_cb_log)
cb_log.grid(row=0, column=0, sticky=W)
cb_log.select()

cb_v_value=BooleanVar()
cb_v=Checkbutton(frame_options, text="/V", variable=cb_v_value)
cb_v.grid(row=0, column=1, sticky=W)
cb_v.select()

cb_e_value=BooleanVar()
cb_e=Checkbutton(frame_options, text="/E", variable=cb_e_value)
cb_e.grid(row=0, column=2, sticky=W)
cb_e.select()

cb_np_value=BooleanVar()
cb_np=Checkbutton(frame_options, text="/NP", variable=cb_e_value)
cb_np.grid(row=0, column=3, sticky=W)
cb_np.select()

cb_hashcheck_value=BooleanVar()
cb_hashcheck=Checkbutton(frame_options, text="Hash Check", variable=cb_hashcheck_value)
cb_hashcheck.grid(row=1, column=0, sticky=W, columnspan=3)

# Console
frame_console=LabelFrame(root, text="Console", padx=20, pady=20)
frame_console.pack(fill="both", expand=True, padx=5, pady=5)

## Log Display
text_console=Text(frame_console, height=15)
text_console.grid(row=0, column=0, sticky="w")


# Done
frame_done=LabelFrame(root, padx=20)
frame_done.pack(side="bottom", fill="both", expand=True, padx=5, pady=5)

## Run button
def func_btn_run():
	text_console.delete("1.0", END)

	path_src=entry_src.get().replace("/", "\\")
	path_dest=entry_dest.get().replace("/", "\\")
	path_log=entry_log.get().replace("/", "\\")
	command=["ROBOCOPY", "{}".format(path_src), "{}".format(path_dest)]

	if cb_log_value.get():
		log_filename=os.path.split(path_src)[1]
		log_filepath="{LOG_PATH}\{LOG_FILENAME}.txt".format(LOG_PATH=path_log, LOG_FILENAME=log_filename)
		command.append("/LOG:{LOG_FILEPATH}".format(LOG_FILEPATH=log_filepath))
	if cb_e_value.get():	command.append("/E")
	if cb_v_value.get():	command.append("/V")
	if cb_np_value.get():	command.append("/NP")
	
	text_console.delete("1.0", END)
	text_console.insert(END, " ".join(command)+"\n")
	with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE) as p:
		for line in p.stdout:
			line=line.decode("cp949")
			line=line.replace("\r","")
			text_console.insert(END, line)

	text_console.insert(END, "\n[Done] Robocopy completed")

	if cb_hashcheck_value.get():
		path_hash=log_filepath.replace(".txt", "_hash.txt")

		start_hashcheck=datetime.datetime.now()
		text_console.insert(END, "\n[Start] Hash compare ({})\n".format(start_hashcheck.strftime("%Y/%m/%d %H:%M:%S")))

		hash_src=get_dic_hash(path_src)
		hash_dest=get_dic_hash(path_dest)

		subhash_src=dict()
		for k, v in hash_src.items():	subhash_src[k.replace(path_src+"\\", "")]=v
		subhash_dest=dict()
		for k, v in hash_dest.items():	subhash_dest[k.replace(path_dest+"\\", "")]=v
		
		cnt_match=0
		cnt_mismatch=0
		for path, hash in subhash_src.items():
			if subhash_dest[path]==hash:
				text_console.insert(END, "- [MATCH] : ")
				del subhash_dest[path]
				cnt_match+=1
			else:
				text_console.insert(END, "- [NOT MATCH] : ")
				cnt_mismatch+=1
			text_console.insert(END, "{} : {}\n".format(path, hash))

		text_console.insert(END, "\nMatched : {}\n".format(cnt_match))
		text_console.insert(END, "Mismatched : {}\n\n".format(cnt_mismatch))

		end_hashcheck=datetime.datetime.now()
		text_console.insert(END, "\n[Done] Hash compare ({})\n".format(end_hashcheck.strftime("%Y/%m/%d %H:%M:%S")))

		with open(path_hash, "w") as fd:
			fd.write(text_console.get("1.0", END))

btn_run=Button(frame_done, text="Run", command=func_btn_run, width=4, height=1)
btn_run.grid(row=0, column=0)

root.mainloop()
