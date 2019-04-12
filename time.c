
/* Ficheiro: time.c **/

/* Descri��o:
   Cont�m fun��es para permitir a marca��o de tempo, tendo por base uma
  interrup��o que ocorre a cada 1ms.  (:avr)
   Permite marcar tempo usando como unidade 1ms, 10ms, 100ms, 1s, etc
*/
/* Autor: Renato Jorge Caleira Nunes */


/*  Historial:
-
*/ /* ::hist */


/*  Notas:
:cfg - Assinala op��es de configura��o
:avr - Assinala particularidades ligadas ao tipo de microcontrolador usado
:init - Assinala particularidades ligadas � inicializa��o de vari�veis
ATT - Assinala uma particularidade a ter em aten��o
!!  - Assinala uma instru��o que n�o deve ser alterada
:err - Assinala um erro interno
cast - Assinala um cast
:OLD - C�digo antigo desactivado
:dbg - Assinala c�digo usado para debug

:tick - Relacionado com unidade de marca��o de tempo
*/



#include <stdio.h>
#include <stdint.h>  /* uint8_t, ... */


#define _TIME_TASK_


/* includes globais */

#include "var_types.h"
#include "node.h"


/* includes globais do compilador WinAVR */

#include <avr/io.h>
#include <avr/interrupt.h>


/* includes espec�ficos deste m�dulo */

#include "main_tasks.h"  /*:inc*/



  /*:cfg  ATT: timers of 1 ms and 10 ms are always available */
			  /*   0=do not use, 1=use */
#define TIME_USE_50MS_TIMERS   0  /*##:cfg ::07 */
#define TIME_USE_100MS_TIMERS  0  /*##:cfg*/
#define TIME_USE_1S_TIMERS     0  /*##:cfg*/
#define TIME_USE_1MIN_TIMERS   0  /*##:cfg  ATT: requires 1s timers */


								/* :tick */
static uint8 TIME_curr_time; /* incrementado por cada interrup��o de 1 ms */
static uint8 TIME_last_time;



/* Inicializa o Timer que fornece o rel�gio de sistema (1ms) (:tick).
   AT8515: Usa Timer/counter 0 (8 bits). Mudei prescaler (19/04/2018) e TCNT0
  para funcionar a 1ms (:tick) (mantive c�digo original que usava 200us).
   ATmega328: Usa o Timer/Counter 0 (8 bits) (p.125) (mudei valores para
  funcionar a 1ms (:tick) (mantive c�digo original que usava 200us).
+------------------------------------------------------------------------*/
void /**/TIME_init(void) /*:avr*/
{

/* ATmega328 */

  /* desnecess�rio pois o reset for�a a 0 */
  //##TIFR0 |= 0x02; /* Timer/Counter0 Interrupt Flag Register (p.148) */
    /* limpa a flag "Timer/Counter0 Compare Match A" interrupt (OCF0A) */

  TCCR0B |= 0X03; /* Timer/Counter Control Register (p.141) */
	/* clock select: CLK/64 (16MHz/64=250KHZ -> 4us) */
 	
  OCR0A = 250; /* 250 x 4us (ver acima) = 1ms (:tick) */ /*::02*/ /*:cfg*/

  TIMSK0 |= 0x02; /* Timer/Counter Interrupt Mask Register (p.143) */
	/* enable "Timer/Counter0 Compare Match A" interrupt */


#if 0  /*## desnecess�rio; compilador inicializa vars globais a 0 */ /*:init*/
  TIME_curr_time = 0;
  TIME_last_time = 0;
#endif

}



/* Rotina de tratamento da interrup��o "Compare Match A" do timer 0.
  (A declara��o da rotina est� de acordo com o compilador WinAVR / avr-gcc).
   � gerada uma interrup��o a cada 1ms (:tick), assumindo um cristal de 16MHz
+------------------------------------------------------------------------*/
ISR(TIMER0_COMPA_vect) /*:avr*/ /*::08*/
{
  OCR0A += 250; /* (:tick) (p.146) ver >>:02 */ /*:cfg*/

  ++TIME_curr_time;
}



#define TIME_10MS_N1MS    10  /* 10 ms (10*1ms) :tick */
#define TIME_50MS_N10MS    5  /* 50 ms (5*10ms) */
#define TIME_100MS_N10MS  10  /* 100 ms (10*10ms) */
#define TIME_1S_N10MS    100  /* 1 s (100*10ms) */
#define TIME_1MIN_N1S     60  /* 1 min (60*1s) */


/* Tarefa que trata da actualiza��o das vari�veis das tarefas que
  contabilizam a passagem do tempo. Essas vari�veis s�o designadas de timers.
  Notar que os timers s�o actualizados em tempo de tarefa e n�o em tempo
  de interrup��o. Se houver necessidade de marcar tempo numa parte de c�digo
  que esteja em ciclo (eventualmente) infinito (por exemplo, numa espera
  activa), a vari�vel em quest�o necessita ser actualizada directamente na
  rotina de interrup��o - ver >>:04.
   A unidade de base de marca��o de tempo � 1ms (:tick) (antes era 200us).
  Permite a marca��o de tempo em unidades de 1ms (o valor de base) (:tick) e
  10ms (existe sempre!!). Pode marcar tamb�m em unidades de 50ms, 100ms, 1s e
  1min dependendo da configura��o usada; ver >>:07. 
+------------------------------------------------------------------------*/
void /**/TIME_task(void)
{
  uint8 aux_t;
  uint8 elapsed_time; /* N x 1ms (:tick = 1 ms) */

  static uint8 t10ms_n1ms = 0; /* 10 ms is always available */

#if TIME_USE_50MS_TIMERS
  static uint8 t50ms_n10ms = 0;
#endif
#if TIME_USE_100MS_TIMERS
  static uint8 t100ms_n10ms = 0;
#endif
#if TIME_USE_1S_TIMERS
  static uint8 t1s_n10ms = 0;
#endif
#if TIME_USE_1MIN_TIMERS
  static uint8 t1min_n1s = 0; /* ATT: requires 1s timers */
#endif


    /* nesta abordagem (19/04/2018) evito desactivar interrup��es */
  aux_t = TIME_curr_time; /* apenas leitura; interrup��o a meio n�o afecta */
  elapsed_time = aux_t - TIME_last_time;
  TIME_last_time = aux_t;



/* Timers de  1ms  :tick (::1ms)*/
	/* var char:  1-255 => 1ms - 255ms (~0.25s) */
	/* var int: 1-65535 => 1ms - 65535ms (~65.5s) */
								/* 1 ms **/

  /*MMM_timer += elapsed_time;*/ /* unit = 1 ms */

// #include "time_1ms.c"  /*##:inc*/



/* Timers de  10ms (::10ms)*/
	/* var char:  1-255 => 0.01s - 2.55s */
	/* var int: 1-65535 => 0.01s - 655.35s (~10.9m) */

  t10ms_n1ms += elapsed_time;
  if(t10ms_n1ms >= TIME_10MS_N1MS)
  {
    t10ms_n1ms -= TIME_10MS_N1MS; /*!!*/
								/* 10 ms **/

    /*++MMM_timer;*/ /* unit = 10 ms */

    #include "time_10ms.h"  /*##:inc*/



#if TIME_USE_50MS_TIMERS  /* [  Timers de 50ms (necessita de 10 ms) (::50ms) */
	/* var char:  1-255 => 0.05s - 12.75s */
	/* var int: 1-65535 => 0.05s - 3276.75s (~54.6m) */

    ++t50ms_n10ms;
    if(t50ms_n10ms >= TIME_50MS_N10MS)
    {
      t50ms_n10ms = 0;
						/* 50 ms  (5*10ms) **/
      /*++MMM_timer;*/ /* unit = 50 ms */


      //#include "time_50ms.c"  /*##:inc*/

    }
#endif /* ] */



#if TIME_USE_100MS_TIMERS  /* [ Timers de 100ms (necessita de 10 ms) (::100ms)*/
	/* var char:  1-255 => 0.1s - 25.5s */
	/* var int: 1-65535 => 0.1s - 6553.5s (~109m, ~1.8h) */

    ++t100ms_n10ms;
    if(t100ms_n10ms >= TIME_100MS_N10MS)
    {
      t100ms_n10ms = 0;
						/* 100 ms  (10*10ms) **/
      /*++MMM_timer;*/ /* unit = 100 ms */


     // #include "time_100ms.c"  /*##:inc*/

    }
#endif /* ] */



#if TIME_USE_1S_TIMERS  /* [  Timers de 1s (necessita de 10 ms) (::1s) */
					/* (precis�o: ver >>:00) */
/* var char:  1-255 => 1s - 255s (~4.2m) */
/* var int: 1-65535 => 1s - 65535s (~1092m, ~18.2h) */

    ++t1s_n10ms;
    if(t1s_n10ms >= TIME_1S_N10MS)
    {
      t1s_n10ms = 0;
						/* 1 s  (100*10ms) **/
      /*++MMM_timer;*/ /* unit = 1 s */


      #include "time_1s.h"  /*##:inc*/



#if TIME_USE_1MIN_TIMERS  /* [  Timers de 1min (necessita de 1 s) (::1min) */
	/* var char:  1-255 => 1m - 255m (~4.2h) */
	/* var int: 1-65535 => 1m - 65535m (~1092h, ~45.5d) */

      ++t1min_n1s;
      if(t1min_n1s >= TIME_1MIN_N1S)
      {
        t1min_n1s = 0;
						/* 1 min  (60*1s) **/
        /*++MMM_timer;*/ /* unit = 1 min */


       // #include "time_1min.c"  /*##:inc*/

      }
#endif /* ] */ /* 1 min */
    }
#endif /* ] */ /* 1 s */
  }
}



/* Fim do ficheiro time.c **/
/* Autor: Renato Jorge Caleira Nunes */
