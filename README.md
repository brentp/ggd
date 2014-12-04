GGD. Test

Note: recipes for datasets retrieved from https://github.com/arq5x/ggd-recipes

Examples
========

Get CpG islands for human build 37 from UCSC 

	$ python ggd.py install ucsc.human.b37.cpg
    searching for recipe: ucsc.human.b37.cpg
    found recipe: ucsc.human.b37.cpg
    installed ucsc.human.b37.cpg

    $ ls -1
    ucsc.human.b37.cpg

Get CpG islands for human build 38 from UCSC and rename file

	$ python ggd.py install ucsc.human.b38.cpg
    searching for recipe: ucsc.human.b38.cpg
    found recipe: ucsc.human.b38.cpg
    installed ucsc.human.b38.cpg

    $ ls -1
    ucsc.human.b37.cpg
    ucsc.human.b38.cpg

Get Clinvar VCF and Tabix index for human build 37 from NCBI

    $ python ggd.py install ncbi.human.b37.clinvar
    searching for recipe: ncbi.human.b37.clinvar
    found recipe: ncbi.human.b37.clinvar
    installed ncbi.human.b37.clinvar

    $ ls -1
    ucsc.human.b37.cpg
    ucsc.human.b38.cpg
	clinvar-latest.vcf.gz
	clinvar-latest.vcf.gz.tbi


Get ExAC VCF and Tabix index for human build 37 from ExAC website (slower)

	$ python ggd.py install misc.human.b37.exac
    searching for recipe: misc.human.b37.exac
    found recipe: misc.human.b37.exac
    installed misc.human.b37.exac

    $ ls -1
    ucsc.human.b37.cpg
    ucsc.human.b38.cpg
	clinvar-latest.vcf.gz
	clinvar-latest.vcf.gz.tbi
    ExAC.r0.2.sites.vep.vcf.gz
    ExAC.r0.2.sites.vep.vcf.gz.tbi

Try to install a recipe that doesn't exist (nearly everything)

	$ python ggd.py install ucsc.human.b38.dbsnp
    searching for recipe: ucsc.human.b38.dbsnp
    could not find recipe: ucsc.human.b38.dbsnp
    exiting.


Dependencies
============
We will try to minimize these as much as possible.

1. Mysql
2. Curl
3. pyyaml
4. Python 2.7
5. Tabix
