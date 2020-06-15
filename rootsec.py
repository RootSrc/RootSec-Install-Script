from utils.color import Color
from time import sleep
import os, sys, logging, time, subprocess

'''
	Init Log File under rootsec.latest.log
'''
logging.basicConfig(filename='rootsec.latest.log',
				filemode='w',
				format='%(asctime)s : %(message)s',
				datefmt='%Y-%m-%d %H:%M:%S',
				level=logging.DEBUG)

def ask(question):
	print('\n')
	Color.writenolog('	{?} ')
	if (input('Would you like to %s (Y/N)? ' % question) == ('y' or 'Y')):
		print('\n')
		return True;


'''
	Ask to install the SecLists and other Wordlists.
'''
def install_sec_list():
	Color.println('	{?} Where would you like to install the sources? : ')
	location = input('')
	if ask('use this location: %s' % location):
		os.mkdir(location)
		os.system('wget -c https://github.com/danielmiessler/SecLists/archive/master.zip -O {0}/SecList.zip && unzip {0}/SecList.zip -d {0} && rm -f {0}/SecList.zip'.format(location))
	return

'''
	Config File Reading
'''
def getCandidates(name, filename, p_names):
	block = False
	candidates = []
	if p_names:
		candidates = {}
	with open(filename,"r") as file:
		for ln in file:
			if name in ln:
				block = True
			if block:
				if ln.startswith('}'):
					return candidates

				if ln.lstrip().startswith("[+]"):
					if p_names:
						candidates[ln[8:-1].rpartition('/')[-1].lower()] = ln[8:-1]
						continue
					candidates.append(ln[8:-1])

'''
	Default Install Location: /opt/
		- TODO: Auto Install into /usr/share/local, 755
'''

def install_git_repo():
	candidates = getCandidates('GitHub', 'candidates.txt', True)

	for name in candidates.keys():
		currentName = candidates.get(name)
		Color.writetoline('\n{+} Installing %s.. ' % currentName)

		proc = subprocess.Popen(['git', 'clone', currentName, '/opt/' + name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout,stderr = proc.communicate()
		stdout = str(stdout)
		stderr = str(stderr)

		if stdout.startswith('b\"fatal:' or 'b\"error:') or stderr.startswith('b\"fatal:' or 'b\"error:'):
			Color.writetoline('{-} Installing %s...' % currentName)
			Color.write('\n           {-} An Error Occured While Installing %s, The error persists below:' % name)
			Color.write('			{-} %s {W}' % stdout[2:-3])
			print('\n\n')

			if ask('continue'):
				print('\n\n')
				continue
			else:
				print('\n\n')
				sys.exit()

		Color.println('\n	{?} Checking if %s needs any extra attention..' % name)
		for files in os.listdir('/opt/%s' % name):
			files = str(files).lower()
			if files == ('requirements.txt' or 'make' or 'makefile' or 'setup.py'):
				Color.writetoline('	{+} %s requires additional setting up, doing that now.' % name)
				Color.write('\n		{+} Found %s file to install.. Doing that now.\n' % files)

				if files == 'requirements.txt':
					os.system('python3 -m pip install -r /opt/%s/requirements.txt' % name)
					os.system('python2 -m pip install -r /opt/%s/requirements.txt' % name)
				elif files == 'setup.py':
					os.system('python /opt/%s/setup.py build install' % name)
				elif files == 'make' or 'makefile':
					os.system('./opt/%s/configure')
					os.system('/opt/%s/make')
					os.system('/opt/%s/make install')
				break
		print('\n')
		Color.write('		{+} Successfully installed %s into /opt/%s \n' % (name, name))


'''
	Install Apt Packages and sources
'''
def install_sources():
	Color.log('Writing GPG keys and Installing Kali Sources..')
	try:
		Color.write('	{?} Attempting to install Kali Sources..\n\n')
		os.system('apt-key adv --keyserver hkp://keys.gnupg.net --recv-keys 7D8D0BF6')
		#os.system('wget -qO - https://archive.parrotsec.org/parrot/misc/parrotsec.gpg | apt-key add -')
		f = open('/etc/apt/sources.list.d/rootsec-kali.list', 'w')
		f.write('# Installed By RootSec Install Script\ndeb http://http.kali.org/kali kali-rolling main non-free contrib')
		f.close()
		os.system('apt-get update -o Dir::Etc::sourcelist="sources.list.d/rootsec-kali.list" -o Dir::Etc::sourceparts="-" -o apt::Get::List-Cleanup="0"')
		Color.log('Completed installing of Kali Sources..')
		Color.write('\n\n	{+} Completed install of Kali Sources!')
	except IOError:
		Color.log(IOError)
		Color.exception(IOError)
	return

def kali_metas():
	clear()
	banner()
	Color.write('	{!} For now this is all the Meta Packages that could be found / or are useful, until I update it.')
	options = [('99', 'Continue')]

	from core.metapackages import packages

	count = 0
	for item in packages.items():
		count += 1
		options.append((str(count), str(item[0]).upper()))

	step = 1
	poptions = int(len(options))
	for package in range(1, poptions):
		if step == 1:
			option_str = ('         {G}{D}[{W}{G}%s{D}]{W} : %s' % (options[package][0], options[package][1]))
			if len(option_str) < 66:
				Color.printlnnolog('\n		' + f'{option_str: <77}')
		if step == 2:
			Color.printlnnolog('{G}{D}[{W}{G}%s{D}]{W} : %s\n' % (options[package][0], options[package][1]))
			step = 1
			continue
		step = 2

	Color.writenolog('\n							{G}{D}[{W}{G}%s{D}]{W}{G} :{W} %s {W}' % (options[0]))
	Color.println('\n	{+} Please Choose an Option: ')

	try:
		choice = int(input(''))
		if choice == 99:
			return
		if choice not in range(1, poptions):
			Color.write('	{-} Not a viable option, try again')
			raise ValueError

		option = str(options[choice][1]).lower()
		for apt_package in packages.get(option):
			if apt_package in packages.keys():
				Color.log('Found Dependancy: ' + apt_package + ' installing now..')
				Color.write('\n\n\n		{!} %s is required for this Meta Package \n\n\n' % apt_package)
				for depend in packages.get(apt_package):
					os.system('apt-get install -y %s' % depend)
				continue
			try:
				Color.log('Installing apt-package ' + apt_package)
				os.system('apt-get install %s -y' % apt_package)
			except:
				Color.println('')
	except ValueError:
		Color.write('	{-} Please Select an number from the options above')
		time.sleep(1)
		return kali_metas()
	Color.write('\n\n		{+} Cleaning up extra Packages')
	time.sleep(3)
	os.system('apt autoremove -y')

	Color.write('		\n\n{+} Completed installing: ' + option)
	time.sleep(5)
	return kali_metas()

'''
	Print Banner
'''
def banner():
	Color.log('Printing Banner..')

	print('\n\n\n\n')
	Color.writenolog('                       {C}############################\n')
	Color.writenolog('                     {G}RootSec Toolin\' Up Install Script\n')
	Color.writenolog('                       {C}############################')
	print('\n\n\n')


'''
	Clears Screen
'''
def clear():
	Color.log('Clearing Screen..')
	os.system('clear')

'''
	Loads Pre Requisites
		- TODO: Remove internet check and allow only when needing internet access.
'''
def check_prereq():
	Color.log('Check pre-reqs..')
	banner()
	Color.log('Checking perms..')
	Color.println('         {?} Checking Proper Permissions..')

	if os.geteuid() != 0:
		Color.write('{-} You need root permissions to run this script.')
		sys.exit()
	Color.writetoline('     {+} Proper Permissions Verified!')

	import socket
	Color.log('Checking Internet Connection..')
	try:
		print('\n\n')
		Color.println(' {?} Checking Internet Connection..')
		socket.create_connection(("www.github.com", 80))
	except OSError:
		Color.log('No internet connection!')
		Color.writetoline('     {-} An active internet connection is needed to run this script!' )
		Color.write('\n         {!}{C} This Check will change later on!{W}\n\n')
		sys.exit()
	Color.writetoline('     {+} You have internet connection!')

	Color.log('Checking if pip2 and pip3 is installed..')
	try:
		print('\n\n')
		Color.println('     {?} Checking if PIP 3 is installed..')
		test = subprocess.Popen(['python3', '-m','pip', '-V'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout,stderr = test.communicate()

		Color.write(str(stdout)[2:-3])

		if 'no module' in str(stdout).lower():
			raise ModuleNotFoundError('There was a problem getting PIP 3')

		Color.println('	      {+} PIP 3 seems to be installed!')

		print('\n\n')
		Color.println('     {?} Checking if PIP 2 is installed..')
		test = subprocess.Popen(['python2', '-m','pip', '-V'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		stdout, stderr = test.communicate()

		Color.write(str(stdout)[2:-3])

		if 'no module' in str(stdout).lower():
			raise ModuleNotFoundError('There was a problem getting PIP 2')

		Color.println('	      {+} PIP 2 seems to be installed!')

	except (ImportError or ModuleNotFoundError) as e:
		Color.writetoline('     {-} Error getting pip. Is it installed correctly?')
		Color.write('\n         {-} %s \n{W}' % str(e))
		sys.exit()

	Color.log('All seems good here.')
	time.sleep(5)
	clear()


'''
	Main Portion:
		- TODO: Organize code
'''

def main():
	clear()
	Color.println('{?} Loading Script..')

	check_prereq()

	Color.println('{+} Loading Script..Done!')
	banner()


	if ask('install SecLists'):
		install_sec_list()

	Color.printlnnolog('\n		{!} Sources Might Be Required to Install Meta Packages!')
	if ask('install Kali/Parrot Sources'):
		install_sources()

	if ask('install Kali Meta Packages'):
		kali_metas()

	if ask('install potentially extra Tools?'):
		install_git_repo()
	print('\n\n')

'''
	Exit prog gracefully,
		- TODO: Clean Up anything, nothing right now
'''
def exit_gracefully(sig, frame):
	clear()
	banner()
	Color.log(Color.println('\n\n{?} SIGINT recieved, Exiting Gracefully..'))
	Color.writetoline('{+} SIGING recieved, Exiting Gracefully..Done \n\n{W}')
	sys.exit(0)

'''
	If Main, Listens for CTRL+C requests.
'''
if __name__ == '__main__':
	import signal
	signal.signal(signal.SIGINT, exit_gracefully)
	main()

