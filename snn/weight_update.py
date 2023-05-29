import matplotlib.pyplot as plt

parent_folder = 'tmp/'

ifns = ['ifn_l_ebn', 'ifn_l_ibn', 'ifn_lr_ebn', 'ifn_r_ebn', 'ifn_r_ibn', 'ifn_rl_ebn', 'ifn_u_ebn', 'ifn_d_ebn']
ver_motor = ['mn_u_ibn', 'mn_d_ibn', 'mn_u_tncv', 'mn_d_tncv', 'mn_u_tnv', 'mn_d_tnv', 'mn_u_tnvv', 'mn_d_tnvv']
hor_motor = ['s1_r_mn_lr_tnvv', 's1_l_mn_ll_ibn', 's1_l_mn_ll_tncv', 's1_r_mn_rr_ibn', 's1_l_mn_ll_tnv', 's1_r_mn_rr_tncv', 's1_l_mn_ll_tnvv', 's1_r_mn_rr_tnv', 's1_r_mn_rr_tnvv', 's1_l_mn_rl_ibn', 's1_l_mn_rl_tncv', 's1_l_mn_rl_tnv', 's1_l_mn_rl_tnvv', 's1_r_mn_lr_ibn', 's1_r_mn_lr_tncv', 's1_r_mn_lr_tnv', 's2_l_mn_rl_tnv', 's2_l_mn_rl_tnvv', 's2_r_mn_lr_ibn', 's2_r_mn_lr_tncv', 's2_r_mn_lr_tnv', 's2_r_mn_lr_tnvv', 's2_l_mn_ll_ibn', 's2_l_mn_ll_tncv', 's2_r_mn_rr_ibn', 's2_l_mn_ll_tnv', 's2_r_mn_rr_tncv', 's2_l_mn_ll_tnvv', 's2_r_mn_rr_tnv', 's2_r_mn_rr_tnvv', 's2_l_mn_rl_ibn', 's2_l_mn_rl_tncv', 's3_l_mn_ll_tncv', 's3_r_mn_rr_ibn', 's3_l_mn_ll_tnv', 's3_r_mn_rr_tncv', 's3_l_mn_ll_tnvv', 's3_r_mn_rr_tnv', 's3_r_mn_rr_tnvv', 's3_l_mn_rl_ibn', 's3_l_mn_rl_tncv', 's3_l_mn_rl_tnv', 's3_l_mn_rl_tnvv', 's3_r_mn_lr_ibn', 's3_r_mn_lr_tncv', 's3_r_mn_lr_tnv', 's3_r_mn_lr_tnvv', 's3_l_mn_ll_ibn', 's4_r_mn_lr_ibn', 's4_r_mn_lr_tncv', 's4_r_mn_lr_tnv', 's4_r_mn_lr_tnvv', 's4_l_mn_ll_ibn', 's4_l_mn_ll_tncv', 's4_r_mn_rr_ibn', 's4_l_mn_ll_tnv', 's4_r_mn_rr_tncv', 's4_l_mn_ll_tnvv', 's4_r_mn_rr_tnv', 's4_r_mn_rr_tnvv', 's4_l_mn_rl_ibn', 's4_l_mn_rl_tncv', 's4_l_mn_rl_tnv', 's4_l_mn_rl_tnvv', 'l_mn_ll_ibn', 'r_mn_lr_ibn', 'l_mn_ll_tncv', 'r_mn_lr_tncv', 'l_mn_ll_tnv', 'r_mn_lr_tnv', 'l_mn_ll_tnvv', 'r_mn_lr_tnvv', 'l_mn_rl_ibn', 'r_mn_rr_ibn', 'l_mn_rl_tncv', 'r_mn_rr_tncv', 'l_mn_rl_tnv', 'r_mn_rr_tnv', 'l_mn_rl_tnvv', 'r_mn_rr_tnvv', ]
ebns = ['ebn_d_llbn', 'ebn_u_llbn', 'ebn_l_ibn', 'ebn_l_opn', 'ebn_lr_llbn', 'ebn_r_ibn', 'ebn_r_llbn', 'ebn_rl_llbn', 'ebn_r_opn']
tns = ['tn_l_ibn', 'tn_lr_ebn', 'tn_r_ebn', 'tn_r_ibn', 'tn_rl_ebn', 'tn_rl_ibn', 'tn_d_ebn', 'tn_u_ebn', 'tn_l_ebn']
llbns = ['llbn_rl_ifn', 'llbn_u_ifn', 'llbn_d_ifn', 'llbn_l_ifn', 'llbn_lr_ifn', 'llbn_r_ifn']
ibns = ['ibn_l_ibn', 'ibn_l_opn', 'ibn_r_ebn', 'ibn_r_ibn', 'ibn_r_opn']
opn = ['opn_ibn_c', 'opn_ibn_i']

# fig.suptitle('Weight Update Horizontal')

# for i, filename in enumerate(files):
# 	plt.subplot(len(files), 1, i+1)
# 	dat = [float(x.replace('\n', '')) for x in open(parent_folder + 'tmp_1/' + filename).readlines()]
# 	plt.plot(dat, 'b')
# 	dat = [float(x.replace('\n', '')) for x in open(parent_folder + 'tmp_2/' + filename).readlines()]
# 	plt.plot(dat, 'r')
# 	dat = [float(x.replace('\n', '')) for x in open(parent_folder + 'tmp_3/' + filename).readlines()]
# 	plt.plot(dat, 'k')
# 	plt.title(filename)

# fig1 = plt.figure()
# fig1.suptitle('Weight Update Vertical')

# for i, filename in enumerate(ver_files):
# 	plt.subplot(len(ver_files), 1, i+1)
# 	dat = [float(x.replace('\n', '')) for x in open(parent_folder + 'tmp_1/' + filename).readlines()]
# 	plt.plot(dat, 'b')
# 	dat = [float(x.replace('\n', '')) for x in open(parent_folder + 'tmp_2/' + filename).readlines()]
# 	plt.plot(dat, 'r')
# 	dat = [float(x.replace('\n', '')) for x in open(parent_folder + 'tmp_3/' + filename).readlines()]
# 	plt.plot(dat, 'k')
# 	plt.title(filename)

things = [ifns, ver_motor, hor_motor, ebns, tns, llbns, ibns, opn]
for something in things:
	plt.figure()
	for i, filename in enumerate(something):
		dat = [float(x.replace('\n', '')) for x in open(parent_folder + filename).readlines()]
		plt.plot(dat, label=filename)
	plt.legend()

plt.show()
