# Script para ler o tempo da inicializacao e validacao

import os
import re
import sys
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.size'] = 14
import statistics
#from paretochart import pareto


if len(sys.argv) < 2 :
	print("Uso: python3 reader.py fold")
	sys.exit()

fold = sys.argv[1]
if not os.path.exists(fold) :
	print("Arquivo", fold, "não encontrado.")
	sys.exit()

check = "Initialization time"
check2 = "Validation time"

batch = 256
exp = 1
machine = 1
epoch = 0

family = 2
machine_true = machine
i = 0
k = 0

total_images = 40512
first_valid = True
second_valid = True
init_time = []
second_its = []
valid_time = []
first_valid_time = []


labfile = fold+"/p"+str(family)+".xlarge/result-"+str(machine)+"-"+str(batch)+"-e"+str(exp)+".out"
if not os.path.exists(labfile) :
	print("Arquivo não existe")
while(os.path.exists(labfile)):
	while(os.path.exists(labfile)):

		print("p"+str(family)+"."+str(machine)+"xlarge")
		print("batch\tinitialization time (s)\tstd init time(s)\tFirst Validation time(s)\t std first valid time(s)\tValidation time(s)\tStd validation time(s)")
			
		while(os.path.exists(labfile)):

			while(os.path.exists(labfile)):
				flx = open(labfile, "r")
				line = flx.readline()
				while(line!=""):
					pos = line.find(check)
					if(pos != -1):
						sec = re.findall(r"\b[0-9]+.\w[0-9]*", line)
						ini_time = float(sec[0])
						init_time.append(ini_time)

					else:
						pos = line.find(check2)
						if (pos != -1):
							sec = re.findall(r"\b[0-9]+.\w[0-9]*", line)
							if first_valid:
								first_valid_time.append(float(sec[0]))
								first_valid = False
							elif second_valid:
								val_time = float(sec[0])
								valid_time.append(val_time)
								second_valid = False
				
					line = flx.readline()
				exp = exp + 1
				first_valid = True 
				second_valid = True
				if (machine > 1):
					labfile = fold+"/p"+str(family)+"."+str(machine)+"xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
				else:	
					labfile = fold+"/p"+str(family)+".xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
				#print(labfile)

			# Calculo do tempo completo
			mean_init_time = sum(init_time)/(exp-1)
			mean_valid_time = sum(valid_time)/(exp-1)
			mean_first_valid_time = sum(first_valid_time)/(exp-1)

			std_first_it = statistics.stdev(init_time)
			std_second_it = statistics.stdev(valid_time)
			std_first_valid_time = statistics.stdev(first_valid_time)

			#print(str(batch)+"\t"+format(mean_init_time, '.3'))
			print(str(batch)+"\t"+format(mean_init_time, '.3')+"\t"+format(std_first_it, '.3')+"\t"+format(mean_first_valid_time, '.3')+"\t"+format(std_first_valid_time, '.3')+"\t"+format(mean_valid_time, '.3')+"\t"+format(std_second_it, '.3'))

			init_time.clear()
			valid_time.clear()
			first_valid_time.clear()

			
			batch *= 2
			exp = 1
			machine_true = machine

			if (family == 3):
				machine_true = int(machine/2)
			if machine != 1:
				labfile = fold+"/p"+str(family)+"."+str(machine)+"xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
			else:
				labfile = fold+"/p"+str(family)+".xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
			#print(labfile)
			#else:
			#	labfile = fold+"/p"+str(family)+".xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"


	
		batch = 256
		if machine == 1 or machine == 2:
			machine = 8
		else:
			machine+=8

		machine_true = machine
		if (family == 3):
			machine_true = int(machine/2)
		if (machine > 1):
			labfile = fold+"/p"+str(family)+"."+str(machine)+"xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
		print("----------------------")
		#print(labfile)
	family = family+1
	machine = 2
	machine_true = int(machine/2)
	labfile = fold+"/p"+str(family)+"."+str(machine)+"xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
	#print(labfile)
#plt.plot(tempo, [256, 512, 1024, 2048])
#plt.show()

#plt.xlabel("Batch size")
#axs[2].set(ylabel="Runtime (s)")
#for ax in axs:
#	ax.yaxis.set_tick_params(labelsize=10)
#	ax.set_ylim([0, 350])
#plt.savefig("graphs/estimative2.pdf")
plt.close()
flx.close()
