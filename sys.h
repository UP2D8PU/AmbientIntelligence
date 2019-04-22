
/* Ficheiro: sys.h **/

/* Autor: Renato Jorge Caleira Nunes */


/*  Historial:
-
*/ /* ::hist */


/*  Notas:
:cfg - Assinala op��es de configura��o
ATT - Assinala uma particularidade a ter em aten��o
!!  - Assinala uma instru��o que n�o deve ser alterada
:err - Assinala um erro interno
cast - Assinala um cast
:dbg - Assinala c�digo usado para debug
*/


/* ::define **/


#define SYS_TRUE   1
#define SYS_FALSE  0


#ifndef _SYS_TASK_
/* ::extern vars **/

extern uint8_t SYS_led_timer;  /* 10 ms */


/* public functions **/

void SYS_init(void);
void SYS_task(void);
void SYS_led_num_pulses(uint8_t num_pulses);

#endif


/* Fim do ficheiro sys.h **/
/* Autor: Renato Jorge Caleira Nunes */
