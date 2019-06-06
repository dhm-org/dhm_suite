#ifndef _CAM_COMMANDS_H_
#define _CAM_COMMANDS_H_

#define MAX_CMD_LEN  128

#define  ENA_RECORDING_CMD    "ENABLE_RECORDING"
#define  DISA_RECORDING_CMD   "DISABLE_RECORDING"

typedef struct msg_hdr
{
    unsigned int msg_id;
    unsigned int src_id;

} msg_hdr_t;

typedef struct cmd_msg
{
    msg_hdr_t header;
    char cmd[MAX_CMD_LEN];
} cmd_msg_t;



#endif
