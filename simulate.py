#  Copyright (C) 2015 Marcell Marosvolgyi

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  


import numpy as np
import subprocess

class Gnuplotter(object):
    
    script = """set logscale x 10
                set logscale y 10
                set grid mxtics mytics xtics ytics lt 1 lc rgb 'gray70', lt 1 lc rgb 'gray90'
                set mxtics 10
                set mytics 5

                set boxwidth 8

                set title "{title}" 
                set xlabel "freq[Hz]"
                set ylabel "amp[rel.]"

                set xrange [10:50000]
                set yrange [0.8: 4]
                
                {plot}

                set size 1.0, 1.0
                #set terminal postscript portrait enhanced mono dashed lw 1 "Helvetica" 14 
                #set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 500,500; set zeroaxis;
                #set terminal pngcairo  enhanced font "arial,20" fontscale 1.0 size 1500,1500; 
                #set output "my-plot.png"
                #set terminal pdf
                #set output "my-plot.pdf"
                set term svg enhanced font "arial,20" mouse size 1500,1200
                set output "my-plot.svg"

                replot
                set terminal x11
                set size 1,1

                #pause -1
            """

    def __init__(self):
        myfile = open("gnuplot.scr","w")
        
        script = self.script.format(
                    title = 'Baxandall tone controll; ngspice, Kicad, Python',
                    plot = 'plot "sim0.csv" using 1:2 smooth csplines title "C1 = 15nF" with lines, "sim1.csv" using 1:2 smooth csplines title "C1 = 25nF" with lines'
                )   
        
        myfile.write(script)
        myfile.close()

    def plot(self):
        subprocess.Popen("gnuplot gnuplot.scr", shell=True, stdout=subprocess.PIPE).stdout.read()
        

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
            
        self.C1 = "47n"
        self.C2 = "560p"
            
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
                                        C1  = self.C1,
                                        C2  = self.C2))
        textfile.close()
            
    def simulate(self):
        self.subst()
        subprocess.Popen("ngspice -b tmp.cir -r sim.raw", shell=True, stdout=subprocess.PIPE).stdout.read()
        subprocess.Popen("rm tmp.cir", shell=True, stdout=subprocess.PIPE).stdout.read()

    def raw2csv(self, name):
        dataf = open('sim.raw','r')
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

class Experiments(object):

    def __init__(self):
        pass

    def simB(self):
        sim = Simulator()
        
        sim.bass(0.3)
        sim.treble(0.3)
        sim.mid(0.5)
        
        for i, c in enumerate([15e-9, 25e-9]):
            sim.C1 = str(c)
            sim.simulate()
            sim.raw2csv("sim{0}".format(i))

        return sim

    def simT(self):
        sim = Simulator()
        
        sim.bass(0.4)
        sim.treble(0.4)
        sim.mid(0.5)
        
        for i, c in enumerate([560e-12, 1000e-12]):
            sim.C2 = str(c)
            sim.simulate()
            sim.raw2csv("sim{0}".format(i))

        return sim
        
    def sim2(self):
        sim = Simulator()
        
        sim.bass(0.4)
        sim.treble(0.5)
        sim.mid(0.5)
        
        for i, r in enumerate(np.arange(5000,40000,5000)):
            sim.R1 = str(r)
            sim.R5 = str(r)
            sim.simulate(i)


if __name__ == '__main__':
    gnuplot = Gnuplotter()
    
    experiment = Experiments()
    
    sim = experiment.simB()
    gnuplot.plot()
    
