import json

class Assembler():
    def load_optab(self,optab_dict):
        self.optab = optab_dict

    def run(self,input_file,output_file):
        self.SYMTAB = dict()
        with open('intermediate.bin','w') as f:
            self.pass1(input_file,f)
        with open('symtab.json','w') as f:
            json.dump(self.SYMTAB,f)
        with open('intermediate.bin','r') as f,open('output.o','w') as g:
            self.pass2(f,g)

    def pass1(self,input_file,temp_file):
        LOCCTR = 0
        for line in input_file.readlines():
            line = line.strip().split(' ')
            if (line[0].endswith(':')):
                label = line[0][:-1]
                if label in self.SYMTAB:
                    raise Exception(f'Label redefined - {label}')
                else:
                    self.SYMTAB[label] = LOCCTR
                line = line[1:]
            LOCCTR += self.getSize(line[0])
            print(' '.join(line),file=temp_file)

    def pass2(self,temp_file,output_file):
        for line in temp_file.readlines():
            line = line.strip().split(' ')
            opcode = line[0]
            if self.optab[opcode]['partial']:
                machine_code = self.optab[opcode][line[1]]
                if self.optab[opcode]['argsize']:
                    args = line[2]
            else:
                machine_code = self.optab[opcode]['mcode']
                if self.optab[opcode]['argsize']:
                    args = line[1]
            output_file.write(machine_code)
            if self.optab[opcode]['argsize']:
                if args in self.SYMTAB:
                    args = str(self.SYMTAB[args])
                args = self.getHex(args).zfill(self.optab[opcode]['argsize']*2)
                if len(args) == 4:
                    args = args[2:] + args[:2]
                output_file.write(args)
    
    def getSize(self,opcode):
        return 1 + self.optab[opcode]['argsize']
    
    @staticmethod            
    def getHex(args):
        if not args.endswith('H'):
            args = hex(int(args))[2:]
        else:
            args = args[-1]
        return args.upper()

if __name__ == '__main__':
    a = Assembler()
    with open('optab.json','r') as f:
        d = json.load(f)
        a.load_optab(d)
    with open('input.asm') as f,open('output.o','w') as g:
        a.run(f,g)