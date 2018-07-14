

class  CsvFile(object):
    def __init__(self,fn=None,sep=','):
        self.fn = fn
        self.data = []
        self.header = None
        if self.fn != None:
            self.data , self.header = self.read(self.fn,sep)

    def read(self,fn,sep=',',inplace=False):
        header = None
        data = []

        f = open(fn,'r')
        while True:
            line = f.readline()
            if len(line) == 0:
                break

            line = line.rstrip('\n\r ')
            if len(line) == 0: continue
            line = line.split(sep)
            if not header:
                header = line
            else:
                data.append(dict(zip(header,line)))

        f.close()
        if inplace:
            self.data = data
            self.header = header
            self.fn = fn

        return data, header

    def write(self,filename,sep=',',header=None):
        self.to_csv(filename,self.data,sep,header)

    def to_csv(self,filename,data,sep=',',header=None):
        if len(data) > 0:
            if header is None:
                header = data[0].keys()
            with open(filename,'w') as f:
                f.write(",".join(header) + "\n")
                for d in data:
                    line = [str(d[k]) for k in header ]
                    f.write(",".join(line) + "\n")

    def rows(self,head=None):
        def row_generator():
            i = 0
            end = head
            if head is None:
                end = len(self.data)
            while i < end:
                yield self.data[i]
                i += 1
            raise StopIteration
        return row_generator()



