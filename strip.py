
f=open('nums', 'r')
n=[]
for l in f.readlines():
	if len(l) >0: 
		num=float(l.split('\n')[0].split(' ')[4])
		n.append(num)

i=sum(n)


avg=(i/len(n))-0.001

total=avg*1.8*60*24

print(total)