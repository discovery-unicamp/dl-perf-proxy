# Script para ler o tempo da primeira, segunda e 10 primeiras iterações

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

check = "1 step"
check2 = "2 step"
check3 = "10 steps training"

batch = 256
exp = 1
machine = 1
epoch = 0

family = 2
machine_true = machine
i = 0
k = 0

total_images = 40512
first_ten = True
first_its = []
second_its = []
ten_fis = []


labfile = fold+"/p"+str(family)+".xlarge/result-"+str(machine)+"-"+str(batch)+"-e"+str(exp)+".out"
if not os.path.exists(labfile) :
	print("Arquivo não existe")
while(os.path.exists(labfile)):
	while(os.path.exists(labfile)):

		print("p"+str(family)+"."+str(machine)+"xlarge")
		print("batch\tfirst iteration (s)\tstd fi (s)\tsecond iteration (s)\tstd si (s)\t10 first iterations\tstd 10fi (s)\t")
			
		while(os.path.exists(labfile)):

			while(os.path.exists(labfile)):
				flx = open(labfile, "r")
				line = flx.readline()
				while(line!=""):
					pos = line.find(check)
					if(pos != -1 and first_ten):
						sec = re.findall(r"\d+\.\d+", line)
						first_it = float(sec[0])
						first_its.append(first_it)

					else:
						pos = line.find(check2)
						if (pos != -1 and first_ten):
							sec = re.findall(r"\d+\.\d+", line)
							second_it = float(sec[0])
							second_its.append(second_it)

							first_ten = False
						else:
							pos = line.find(check3)
							if (pos != -1 and first_ten):
								sec = re.findall(r"\d+\.\d+", line)
								ten_fi = float(sec[0])
								ten_fis.append(ten_fi)
								first_ten = False
				
					line = flx.readline()
				exp = exp + 1
				first_ten = True 
				if (machine > 1):
					labfile = fold+"/p"+str(family)+"."+str(machine)+"xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
				else:	
					labfile = fold+"/p"+str(family)+".xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
				#print(labfile)

			# Calculo do tempo completo
			mean_first_it = sum(first_its)/(exp-1)
			mean_second_it = sum(second_its)/(exp-1)
			#mean_first_ten = sum(ten_fis)/(exp-1)

			std_first_it = statistics.stdev(first_its)
			std_second_it = statistics.stdev(second_its)
			#std_first_ten = statistics.stdev(ten_fis)

			#print(str(batch)+"\t"+format(mean_first_it, '.3')+"\t"+format(std_first_it, '.3')+"\t"+format(mean_second_it, '.3')+"\t"+format(std_second_it, '.3')+"\t"+format(mean_first_ten, '.3')+"\t"+format(std_first_ten, '.3'))

			print(str(batch)+"\t"+format(mean_first_it, '.3')+"\t"+format(std_first_it, '.3')+"\t"+format(mean_second_it, '.3')+"\t"+format(std_second_it, '.3'))

			first_its.clear()
			second_its.clear()
			ten_fis.clear()		

			
			batch *= 2
			exp = 1
			machine_true = machine

			if (family == 3):
				machine_true = int(machine/2)
			if machine != 1:
				labfile = fold+"/p"+str(family)+"."+str(machine)+"xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"
			else:
				labfile = fold+"/p"+str(family)+".xlarge/result-"+str(machine_true)+"-"+str(batch)+"-e"+str(exp)+".out"


	
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

