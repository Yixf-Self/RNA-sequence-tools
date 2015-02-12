import os
from subprocess import call


def get_files(path, out= './'):
  annotation_file = '/Users/idriver/Downloads/Mus_musculus_UCSC_mm10/Mus_musculus/UCSC/mm10/Annotation/Archives/archive-2014-05-23-16-05-10/Genes/genes.gtf'
  index_gen_loc = '/Users/idriver/Downloads/mm10/mm10'
  pathlist = []
  for root, dirs, files in os.walk(path):
    if 'fastq' in root:
      pathlist.append([root,files])
  for p in pathlist:
    n = p[0].strip('./').split('_')
    name = n[0]
    result_file = os.path.join(out, name)
    try:
      os.mkdir(result_file)
    except OSError:
      pass
    input_files=''
    for f in p[1]:
      if 'gz' in f:
        f_split = f.split('_')
        r_name = f_split[3]
        en_split = f_split[4].split('.')
        r_num = en_split[0]
        input_files+=os.path.join(os.getcwd(),p[0].strip('./'),f)+' '
    if len(p[1]) > 2:
      in_split = input_files.split(' ')
      name_build = ''
      for i, mul_f in enumerate(in_split):
        if 'gz' in mul_f:
          if i == len(p[1])-1:
            name_build+=mul_f
          elif i < (len(p[1])/2)-1 or i > (len(p[1])/2)-1:
            name_build+= mul_f+','
          elif i ==  (len(p[1])/2)-1:
            name_build+= mul_f+' '
    if len(p[1]) >2:
      final_files = name_build
    else:
      final_files = input_files
    for h, k, l in os.walk(result_file):
      if 'accepted_hits.bam' in l:
        cuff_to_call = '/Users/idriver/Downloads/cufflinks-2.1.1.OSX_x86_64/cufflinks -p 4 -G '+annotation_file+' -o '+result_file+' '+result_file+'/'+'accepted_hits.bam'
        print cuff_to_call
        call(cuff_to_call, shell=True)
        break
      else:
        to_call = 'tophat -p 4 -r 50 -G '+annotation_file+' -o '+result_file+' '+index_gen_loc+' '+final_files
        print to_call
        call(to_call, shell=True)
        cuff_to_call = '/Users/idriver/Downloads/cufflinks-2.1.1.OSX_x86_64/cufflinks -p 4 -G '+annotation_file+' -o '+result_file+' '+result_file+'/'+'accepted_hits.bam'
        call(cuff_to_call, shell=True)

get_files('./', out = '/Users/idriver/RockLab-files/test')