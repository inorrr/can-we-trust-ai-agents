from common import *
if len(sys.argv)!=6:sys.exit(2)
run,name,start,code,count=sys.argv[1:]
s=Stage(run,name);s.started=start;s.inputs=int(count);s.outputs=int(count)
if int(code):s.errors=['One or more component stages failed or were incomplete; inspect component receipts']
s.receipt(int(code))
