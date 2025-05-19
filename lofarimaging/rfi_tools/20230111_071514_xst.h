# LCU obs settings, header file
# Header version 4
beamctl_cmds:
- beamctl --antennaset=LBA_INNER --rcus=0:191 --band=10_90 --beamlets=0:410 --subbands=51:461 --anadir=0.0,0.0,SUN --digdir=0.0,0.0,SUN
filenametime: '20230111_071514'
ldat_type: xst
rcusetup_cmds:
- rspctl --bitmode=8
rspctl_cmds:
- rspctl --xcsubband=120
- rspctl --xcstatistics --integration=1 --duration=1 --directory=/data/home/user1/.cache/ilisa/BSX_data/
