import fnmatch
import os
import csv
import subprocess

def write_file(filename, contents):
    """Write the given contents to a text file.

    ARGUMENTS
    filename (string) - name of the file to write to, creating if it doesn't exist
    contents (string) - contents of the file to be written
    """

    # Open the file for writing
    file = open(filename, 'w')

    # Write the file contents
    file.write(contents)

    # Close the file
    file.close()

    return

def qsub_submit(command_filename, hold_jobid = None, fname = None):
    """Submit the given command filename to the queue.

    ARGUMENTS
    command_filename (string) - the name of the command file to submit

    OPTIONAL ARGUMENTS
    hold_jobid (int) - job id to hold on as a prerequisite for execution

    RETURNS
    jobid (integer) - the jobid
    """

    # Form command
    command = 'qsub'
    if fname: command += ' -N %s' % fname
    if hold_jobid: command += ' -hold_jid %d' % hold_jobid
    command += ' %s' % command_filename

    # Submit the job and capture output.
    import subprocess
    print "> " + command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    print(out)

    # Match job id
    jobid = out.split(' ')[2]

    return int(jobid)


result_file_name = ['results_sca_spc']

path = os.path.join('/netapp/home/idriver', result_file_name[0])

cuffdiff_files_1 = ''
cuffdiff_files_rest = ''

for root, dirnames, filenames in os.walk(path):
    if root.split('/')[-1][0] != 'C':
        for filename in fnmatch.filter(filenames, 'accepted_hits.bam'):
            sample_name = root.split('/')[-1]
            if sample_name[-1] == '1' or sample_name[-1] == '2':
                cuffdiff_files_1 += os.path.join(root, filename)+','
            else:
                cuffdiff_files_rest += os.path.join(root, filename)+' '

labels = 'scapos_spcpos,scaneg_spcpos,scapos_spcneg,scaneg_spcneg'
cuff_diff_files = cuffdiff_files_1.strip(',')+ ' ' + cuffdiff_files_rest.strip(' ')
annotation_file = '/netapp/home/idriver/genes_E_RS.gtf'
index_gen_loc = '/netapp/home/idriver/Norm_mm10_ERCC_RS.fa'
cuff_name = 'cuffdiff4_'+result_file_name[0]
cuffdiff_cmd = 'cuffdiff -p 12 -u --max-bundle-frags 10000000 -L '+labels+' -b '+ index_gen_loc+ ' -o '+cuff_name+' '+annotation_file+' '+cuff_diff_files
print cuffdiff_cmd
mk_dir = 'mkdir -p '+os.path.join('/netapp/home/idriver', cuff_name)
subprocess.call(mk_dir, shell=True)

command = """\
#!/bin/sh
#!/bin/sh
#$ -l arch=linux-x64
#$ -S /bin/bash
#$ -o /netapp/home/idriver/%(cuff_name)s
#$ -e /netapp/home/idriver/error_spc
#$ -cwd
#$ -r y
#$ -j y
#$ -l netapp=10G,scratch=20G,mem_total=40G
#$ -pe smp 12
#$ -R yes
#$ -l h_rt=6:59:00
set echo on
date
hostname
pwd
export PATH=$PATH:${HOME}/bin
PATH=$PATH:/netapp/home/idriver/cufflinks-2.2.1.Linux_x86_64
PATH=$PATH:/netapp/home/idriver/bin/bowtie2-2.2.3
PATH=$PATH:/netapp/home/idriver/bin/samtools-0.1.19_2
PATH=$PATH:/netapp/home/idriver/bin/tophat-2.0.13.Linux_x86_64
PATH=$PATH:/usr/bin/gunzip
export PATH
export TMPDIR=/scratch
echo $TMPDIR
cd $TMPDIR
mkdir %(cuff_name)s

%(cuffdiff_cmd)s
# Copy the results back to the project directory:
cd $TMPDIR
cp -r %(cuff_name)s/* /netapp/home/idriver/%(cuff_name)s
""" % vars()

filename = 'cuffdiff_'+result_file_name[0]+'.sh'
write_file(filename, command)
jobid = qsub_submit(filename, fname=cuff_name)
print "Submitted. jobid = %d" % jobid
# Write jobid to a file.
import subprocess
process = subprocess.Popen('echo %d > jobids' % jobid, stdout=subprocess.PIPE, shell = True)
out, err = process.communicate()
print(out)
