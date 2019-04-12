
/* Ficheiro: sys.c **/

/* Descrição:
   Aplicação de sistema que existe em todos os nós e é responsável por diversas
  funções de gestão como, por exemplo, comando do LED "alive", pulsar do
  watchdog, 
*/

/* Autor: Renato Jorge Caleira Nunes */


/*  Historial:
03/11/2011 - Criação deste módulo. Versão básica do módulo SYS original em
 que apenas pisca o LED e controla o watchdog.
*/ /* ::hist */


/*  Notas:
:cfg - Assinala opções de configuração
:avr - Assinala particularidades ligadas ao tipo de microcontrolador usado
:init - Assinala particularidades ligadas à inicialização de variáveis
ATT - Assinala uma particularidade a ter em atenção
!!  - Assinala uma instrução que não deve ser alterada
:err - Assinala um erro interno
cast - Assinala um cast
:dbg - Assinala código usado para debug
*/



#include <stdio.h>
#include <stdint.h>  /* uint8_t, ... */


#define _SYS_TASK_


/* includes globais */

#include "var_types.h"
#include "node.h"


/* includes globais do compilador WinAVR */

#include <avr/io.h>
#include <avr/interrupt.h>


/* includes específicos deste módulo */

#include "sys.h"



	/* ::define **/

  /* placa ARDUINO: LED "alive" = PB5 */
#define SYS_LED_PORT  PORTB  /* porto B (Arduino) */
#define SYS_LED_DDR    DDRB  /* Data Direction Regist.(DDR) B */

#define SYS_LED_PIN_MASK  0x20  /* PIN5 : 0010 0000 */

  /* não existe watchdog externo no Arduino */



	/* LED "alive" é activo a HIGH (placa ARDUINO) */

#define SYS_LED_TURN_ON    SYS_LED_PORT |= SYS_LED_PIN_MASK
#define SYS_LED_TURN_OFF   SYS_LED_PORT &= ~SYS_LED_PIN_MASK

#define SYS_LED_TOGGLE     SYS_LED_PORT ^= SYS_LED_PIN_MASK




#define SYS_LED_PULSE_TIME   20  /* 200 ms */ /*##:cfg*/ /*::01*/
#define SYS_LED_PAUSE_TIME   50  /* 500 ms */



/* Variáveis globais ::vars **/

uint8 SYS_led_timer;  /* 10 ms */



/* Variáveis locais **/

static uint8 SYS_led_num_toggles, SYS_led_toggle_n; /* ver >>:06 */




/* Atribui o valor adequado a SYS_led_num_toggles que define o número de
  impulsos que o LED "alive" irá emitir.
   SYS_led_num_toggles = ("num_pulses" * 2) - 1.
+------------------------------------------------------------------------*/
void /**/SYS_led_num_pulses(uint8 num_pulses)
{
  SYS_led_num_toggles = (num_pulses << 1) - 1;
}



/* Inicialização da tarefa SYS.
+------------------------------------------------------------------------*/
void /**/SYS_init(void)
{

  /* led init + external watchdog init */

  /* Arduino: o pino do LED "alive" já foi inicializado; Ver avr_init() em
    MAIN.C */


  SYS_led_num_pulses(1);
//  SYS_led_toggle_n = 0; /* Desnecessário */ /*:init*/

//  SYS_led_timer = 0; /* Desnecessário */ /*:init*/
}



/* Tarefa SYS. Apenas controla o led "alive".
+------------------------------------------------------------------------*/
void /**/SYS_task(void)
{

  /* Pulsa LED "alive" */

  if(SYS_led_toggle_n == 0) /*::06*/
  {
    if(SYS_led_timer >= SYS_LED_PAUSE_TIME)
    {
      SYS_LED_TOGGLE;
      SYS_led_timer = 0;
      SYS_led_toggle_n = SYS_led_num_toggles;
    }
  }
  else
  {
    if(SYS_led_timer >= SYS_LED_PULSE_TIME)
    {
      SYS_LED_TOGGLE;
      SYS_led_timer = 0;
      --SYS_led_toggle_n;
    }
  }
}



/* Fim do ficheiro sys.c **/
/* Autor: Renato Jorge Caleira Nunes */

