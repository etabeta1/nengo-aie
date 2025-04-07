SRCS = $(wildcard *.cc)
OBJS = $(SRCS:.cc=.o)

all: $(OBJS)

%.o: %.cc
	${PEANO_INSTALL_DIR}/bin/clang++ ${PEANOWRAP2_FLAGS} -c $< -o ${@F}

clean:
	rm -f *.o

include ../make.defs
