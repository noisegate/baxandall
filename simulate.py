import numpy as np
import subprocess

class Simulator(object):
	
	def __init__(self):
		netlist = open("baxandall.cir")
		self.netlist = netlist.read()
		netlist.close()
		
		self.R1 = "22k"
		self.R2 = "50k"
		self.R3 = "22k"
		self.R4 = "50k"
		self.R5 = "22k"

		self.R8 = "10k" 
		self.R9 = "50k"
		self.R10= "50k"
		self.R11= "10k"
			
		self.R12 = "3.6k"
		self.R13 = "50k"
		self.R15 = "50k"
		self.R16 = "3.6k"
			
			
		self.C1 = "47n"
		self.C2 = "560p"
			
		self.C3 = "22n"
		self.C4 = "5n"
			
		self.filename = "tmp.cir"
		
		self.data = None
		
	def bass(self, f):
		self.R2 = str(f*50000)
		self.R4 = str((1-f)*50000)

	def treble(self, f):
		self.R9 = str(f*50000)
		self.R10 = str((1-f)*50000)
		
	def mid(self,f):
		self.R13 = str(f*50000)
		self.R15 = str((1-f)*50000)
	
			
	def subst(self):
		textfile = open("tmp.cir",'w')
		textfile.write (self.netlist.format(
										R1  = self.R1,
										R2  = self.R2,
										R3  = self.R3,
										R4  = self.R4,
										R5  = self.R5,
										R8  = self.R8,
										R9  = self.R9,
										R10 = self.R10,
										R11 = self.R11,
										R12 = self.R12,
										R13 = self.R13,
										R15 = self.R15,
										R16 = self.R16,
										C1  = self.C1,
										C2  = self.C2,
										C3  = self.C3,
										C4  = self.C4))
		textfile.close()
			
	def simulate(self, i):
		self.subst()
		subprocess.Popen("ngspice -b tmp.cir -r sim{0}.raw".format(i), shell=True, stdout=subprocess.PIPE).stdout.read()
		subprocess.Popen("rm tmp.cir", shell=True, stdout=subprocess.PIPE).stdout.read()

	def plot(self):
		subprocess.Popen("gnuplot gnuplot.scr", shell=True, stdout=subprocess.PIPE).stdout.read()
		
	def raw2csv(self, name):
		dataf = open('sim0.raw','r')
		data = dataf.read()
		dataf.close()
		self.data = data
		
		datalines = data.splitlines()
		
		headerread = False
		freq=0
		amp=0
		xstr=''
		ystr=''
		
		x = []
		y = []
		
		csv = ""
		
		for i, line in enumerate(datalines):
			if headerread:
				el = line.split('\t')
				if (len(el)==3):
					xstr =  "point:{nr} freq:{f}". format(nr = el[0], f = el[2])
					freqstr = el[2].split(",")
					freq = float(freqstr[0])
 				elif (len(el)==2):
					ystr = " -- ampl:{a}".format(a = el[1])
					ampstr = el[1].split(",")
					ampre = float(ampstr[0])
					ampim = float(ampstr[1])
					amp = ampre**2 + ampim **2
				
				newline =  " ".join([str(freq),str(amp)])		
				
				csv = "\n".join([csv, newline])
				
				x.append(freq)
				y.append(amp)
				
			if line.find("Values:"):
				headerread = True
		
		#print csv
		outf = open("{name}.csv".format(name=name),"w")
		outf.write(csv)
		outf.close()

def sim1():
	sim = Simulator()
	
	sim.bass(0.4)
	sim.treble(0.5)
	sim.mid(0.5)
	
	for i, c in enumerate([10e-9]):
		sim.C1 = str(c)
		sim.simulate(i)

	return sim

def sim2():
	sim = Simulator()
	
	sim.bass(0.4)
	sim.treble(0.5)
	sim.mid(0.5)
	
	for i, r in enumerate(np.arange(5000,40000,5000)):
		sim.R1 = str(r)
		sim.R5 = str(r)
		sim.simulate(i)


if __name__ == '__main__':
	sim = sim1()
	sim.raw2csv("sim")
	sim.plot()	
	
