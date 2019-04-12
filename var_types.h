
/* Ficheiro: var_types.h **/
/* Cont�m declara��es de tipos de vari�veis que s�o usados nos v�rios m�dulos. */

/* Autor: Renato Jorge Caleira Nunes */

/*  Historial:
12/09/2013 - Vers�o que usa "typedefs".
*/ /* ::hist */


typedef unsigned char uchar;
typedef unsigned int uint;
typedef unsigned long int ulong;

typedef unsigned char uint8;
typedef unsigned short int uint16;
typedef unsigned long int uint32;

typedef signed char int8;
typedef short int int16;
typedef long int int32;


#if 1  /* contexto PC: um int tem 32 bits */
typedef long int n_int; /* native "int" */
typedef unsigned long int n_uint; /* native "unsigned int" */
#endif


/* Fim do ficheiro var_types.h **/
/* Autor: Renato Jorge Caleira Nunes */

