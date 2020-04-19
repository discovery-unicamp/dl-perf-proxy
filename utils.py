# -*- coding: utf-8 -*-

# Define diversas funcoes de apoio para limpar os notebooks

from __future__ import print_function
import numpy as np
import pymei as pm
import matplotlib.pyplot as plt
import random
import os
import sys
from six.moves import cPickle as pickle
from scipy import ndimage
#import sys


def load_picks(picks_file, time_scale='s'):
	"""Carrega os picks (eventos ou não eventos) de um empilhamento e retorna uma 
		lista de picks no formato (CDP, time (s))
	
	Args:
		picks_file: nome do arquivo que contém as coordenadas dos picks. Assume que cada pick
			no arquivo de texto está na ordem (CDP, tempo)
		time_scale: escala de tempo dos picks. Pode ser:
			's': segundo
			'ms': milissegundo
			'mus': microssegundo

	Retorno:
		picks_list: lista de picks no formato (CDP, tempo), onde tempo está sempre em segundos
			e CDP é um número inteiro
	"""
	if time_scale == 's':
		time_scale = 1.0
	elif time_scale == 'ms':
		time_scale = 1.0e3
	elif time_scale == 'mus':
		time_scale = 1.0e6
	else:
		print("Escala de tempo nao definida, picks nao carregados.")
		return None

	# Carrega os picks do arquivo
	picks = np.loadtxt(picks_file)

	# Acumula picks em uma lista, reescalando o tempo para segundo
	picks_list = []
	for cdp, time in picks:
		time = time / time_scale 
		cdp = int(cdp)
		picks_list.append([cdp, time])
	return picks_list



def picks_to_index(picks_list, traces):
	"""Transforma uma lista de picks em uma lista de coordenadas da matriz
	
	Args:
		picks_list: lista com os picks no formato (tempo (s), CDP)
		traces: todos os traços carregados em um empilhamento. Assume que está ordenado por CDP.

	Retorno:
		picks_coord: coordenada dos picks como índices de uma matriz, onde cada coordenada
			está  no formato (timde_index, cdp_index)
	"""
	# Constrói dicionário que associa um cdp a um índice (pressupõe empilhamento ordenado por CDP)
	cdp_dic = {}
	for index, trace in enumerate(traces):
		# Sanity check: verifica se não há cdp repetido no empilhamento
		cdp = trace.cdp
		if (cdp_dic.has_key(cdp)): print("Atencao: CDP %d repetido no empilhamento." % cdp)
		cdp_dic[cdp] = index
	
	# Transforma os picks em coordenadas
	picks_coord = []
	dt = traces[0].dt	   # intervalo entre amostras (pymei converte sempre para segundos)
	for cdp, time in picks_list:
		time_index = int((time / dt))
		cdp_index = cdp_dic[int(cdp)]
		picks_coord.append([time_index, cdp_index])
	return picks_coord



def load_traces(stack_file):
	"""Carrega todos os traços de um dado sísmico empilhado - extensão .SGY ou .SU e
	ordena por CDP. Imprime também algumas informações sobre o empilhamento

	Args:
		stack_file: nome do arquivo que contém o dado sísmico.

	Retorno:
		traces: lista com os traços ordenados por CDP
	"""

	# Carrega o empilhamento
	try:
		traces = [t for t in pm.load(stack_file)]
		print("Carregando o empilhamento", stack_file)
	except Exception as e:
		print("Nao foi possivel carregar o empilhamento", stack_file, "\n", e)
		return None

	# Ordena por CDP
	traces.sort(key=lambda trace: trace.cdp)
	
	# Imprime algumas informações
	cdp_min = min(traces, key=lambda trace: trace.cdp).cdp
	cdp_max = max(traces, key=lambda trace: trace.cdp).cdp
	ns = traces[0].ns
	dt = traces[0].dt * 1000
	print(len(traces), "tracos:")
	print(" - CDP: [%d - %d]" % (cdp_min, cdp_max))
	print(" - Amostras por traco (ns):", ns) 
	print(" - Tempo entre amostras (dt): %.1f ms" % dt)
	
	return traces



def normalize_as_pic(stack, verbose=True):
	"""Normaliza o empilhamento para o intervalo [0.0 - 1.0] 

	Args:
		stack: numpy.array contendo os dados do empilhamento (sem cabeçalho)
		verbose: se gostaria de imprimir informações pré e pós empilhamento.
				Default: True

	Retorno:
		stack: dado normalizado
	"""
	if (verbose):
		print("Caracteristicas pre-normalizacao:")
		print(" - minimo:", stack.min())
		print(" - maximo:", stack.max())
		print(" - media:", stack.mean())
		print(" - desvio padrao:", stack.std())
	
	# Mapeia linearmente o dado do intervalo [data.min, data.max] para [0.0, 1.0]
	minimum = np.min(stack)
	maximum = np.max(stack)
	stack = (stack - minimum) / (maximum - minimum)

	if (verbose):
		print("\nCaracteristicas pos-normalizacao:")
		print(" - minimo:", stack.min())
		print(" - maximo:", stack.max())
		print(" - media:", stack.mean())
		print(" - desvio padrao:", stack.std())
	return stack

def clip_std(stack, max_std = None):
	""" Realiza um clip no dado por desvio padrao
	Args: 
		stack: numpy.array contendo od dados do empilhamento (sem cabeçalho)
		max_std: valor pelo qual quer multiplicar o desvio padrao para fazer o clip
			Default: None
	"""
	if not max_std is None:
		#Faz o clip do dado
		max = stack.std() * max_std
		min = -max
		stack = np.clip(stack, min, max)
		
		#imprime os novos valores de minimo e maximo do dado
		print("\n Caracteristicas do Clip:")
		print("- minimo:", min)
		print("- maximo:", max)
	  
	return stack



def rms_normalize(stack, verbose=True):
	"""Normaliza o empilhamento traço a traço, a partir do RMS de cada traço.
	Obs: esta eh uma operacao destrutiva, entao se nao quiser corromper o dado original, 
	deve-se passar uma copia do empilhamento.

	Args:
		stack: numpy.array contendo os dados do empilhamento (sem cabecalho)
		verbose: se gostaria de imprimir informacoes pre e pos empilhamento.
				Default: True

	Retorno:
		stack: dado normalizado
	"""
	if (verbose):
		print("Caracteristicas pre-normalizacao:")
		print(" - minimo:", stack.min())
		print(" - maximo:", stack.max())
		print(" - media:", stack.mean())
		print(" - desvio padrao:", stack.std())
	# Para cada traço no empilhamento, calcula o RMS do traço e divide o traço por este valor
	for j in xrange(stack.shape[1]):
		rms = np.sqrt(np.mean(np.power(stack[:,j], 2)))
		stack[:,j] = stack[:,j] / rms
	# Centra o empilhamento na média
	stack = stack - stack.mean()
	if (verbose):
		print("\nCaracteristicas pos-normalizacao:")
		print(" - minimo:", stack.min())
		print(" - maximo:", stack.max())
		print(" - media:", stack.mean())
		print(" - desvio padrao:", stack.std())
	return stack

def std_normalize(stack, verbose=True):
	"""Normaliza o empilhamento pelo desvio padrão 

	Args:
		stack: numpy.array contendo os dados do empilhamento (sem cabeçalho)
		verbose: se gostaria de imprimir informações pré e pós empilhamento.
				Default: True

	Retorno:
		stack: dado normalizado
	"""
	if (verbose):
		print("Caracteristicas pre-normalizacao:")
		print(" - minimo:", stack.min())
		print(" - maximo:", stack.max())
		print(" - media:", stack.mean())
		print(" - desvio padrao:", stack.std())
	
	# Normaliza o dado a partir do 
	mean = np.mean(stack)
	std = np.std(stack)
	stack = stack / std

	if (verbose):
		print("\nCaracteristicas pos-normalizacao:")
		print(" - minimo:", stack.min())
		print(" - maximo:", stack.max())
		print(" - media:", stack.mean())
		print(" - desvio padrao:", stack.std())
	return stack

def range_normalize_std(stack, verbose=True, max_std = None):
	"""Normaliza o empilhamento para um intervalo de [-1,1] com a opcao de dar clip
	no dado de entrada em relacao ao desvio padrao

	Args:
		stack: numpy.array contendo os dados do empilhamento (sem cabeçalho)
		verbose: se gostaria de imprimir informações pré e pós empilhamento.
			Default: True
		max_std: realiza clip do dado multiplicando esse valor pelo desvio padrao
			Defaut: None

	Retorno:
		stack: dado normalizado
	"""
	if (verbose):
		print("Caracteristicas pre-normalizacao:")
		print(" - minimo:", stack.min())
		print(" - maximo:", stack.max())
		print(" - media:", stack.mean())
		print(" - desvio padrao:", stack.std())
	
	#Clip no dado a partir do desvio padrao 
	stack = clip_std(stack, max_std)
	
	# Normaliza o dado para ficar entre o iteralo de [-1,1]
	mean = np.mean(stack)
	maximum = np.max(stack)
	minimum = np.min(stack)
	stack = stack / max(maximum, abs(minimum))

	if (verbose):
		print("\nCaracteristicas pos-normalizacao:")
		print(" - minimo:", stack.min())
		print(" - maximo:", stack.max())
		print(" - media:", stack.mean())
		print(" - desvio padrao:", stack.std())
	return stack


def cut_off_dataset_top(dataset, labels, label, max_height=0.25, max_width= 1.0, min_height= 0, min_width = 0, crop_type='bottom' ):
	"""Normaliza o empilhamento para um intervalo de [-1,1] com a opcao de dar clip
	no dado de entrada em relacao ao desvio padrao

	Args:
		dataset: 
		labels: 
		label: Qual a label que quer setar como verdadeira
		label: realiza clip do dado multiplicando esse valor pelo desvio padrao
		max_height: Porcentagem maxima da imagem que a altura do o retangulo de cutoff pode ter
		min_height: Porcentagem minima da imagem que a altura do o retangulo de cutoff pode ter
		max_width: Porcentagem maxima da imagem que a largura do o retangulo de cutoff pode ter
		min_width: Porcentagem minima da imagem que a largura do o retangulo de cutoff pode ter
		crop_type: Local onde quer fazer o cut off, temos as opções:
			'bottom': Defaut. Faz o cut off na região inferior da imagem
			'top': Faz o cut off na região superior da imagem
			'middle': Faz o cut off na região central da imagem
			
	Retorno:
		stack: dado normalizado
	"""
	dataset_size = len(dataset)
	new_dataset = np.zeros_like(dataset)
	new_labels = np.zeros_like(labels)
		
	new_labels[:, label] = 1.0
		
	mask = np.ones_like(dataset)
   
	for i in range(len(mask)):
		height = random.randint(int(dataset.shape[1] * min_height), int(dataset.shape[1] * max_height))
		width = random.randint(int(dataset.shape[2] * min_width), int(dataset.shape[2] * max_width))		
	
		left = (dataset.shape[2] - width)/2
		right = left + width 
	
		if crop_type == 'bottom':
			bottom = dataset.shape[2]	
			top = bottom - height
		elif crop_type == 'top':
			bottom = height
			top = 0
		elif crop_type == 'middle':
			middle_data = int((dataset.shape[2])/2)
			height = int(height/2)
			
			bottom = middle_data + height
			top = middle_data - height
			
		mask[i, top:bottom, left:right] = 0

	mask = dataset * mask

	new_dataset = np.concatenate((dataset, mask), axis=0)
	new_labels = np.concatenate((labels, new_labels), axis=0)
		
	return new_dataset, new_labels		
	
def flip_dataset(dataset, labels):
	print("Espelhamento das amostras flip")
	dataset_size = dataset.shape[0]
	new_dataset = np.zeros_like(dataset)
	new_labels = np.zeros_like(labels)
		
	
	for i in range(dataset_size):
		new_dataset[i] = np.flip(dataset[i], 1)
		new_labels[i] = labels[i]
	
	return new_dataset, new_labels


def negative_dataset(dataset, labels):
	print("Espelhamento das amostras flip")
	
	dataset_size = len(dataset)
	new_dataset = np.zeros_like(dataset)
	new_labels = np.zeros_like(labels)
		
	new_labels = labels
	
	new_dataset = -1 * dataset
		  
	return new_dataset, new_labels

def clip_seismic_image(seismic_image, clip_percent=1):
	seismic_image_clip = np.clip(seismic_image, seismic_image.min() * clip_percent, seismic_image.max() * clip_percent)
	return seismic_image_clip

def generate_samples(stack, window_size, picks_coord, label=0, num_classes=2, verbose=True):
	"""Extrai as amostras rotuladas do empilhamento.

	Args:
		stack: empilhamento (numpy.array)
		window_size: tamanho da janela ao redor do pick
		picks_coord: coordenadas da matriz referente ao rótulo
		label: rótulo (eventou ou não evento)
		num_classes: número de classes do problema
		flip: se deve ou não duplicar cada amostra usando espelhamento

	Retorno:
		dataset: conjunto de amostras (janelas) centradas nas picks_coords
		labels: conjunto de rótulos referentes a cada janela, no formato one-hot
	"""
	half_size = window_size // 2 # Divisão inteira
	dataset_size = len(picks_coord)
	# Determina formato para dado 2D ou 3D
	if (len(stack.shape) == 2): shape = (dataset_size, window_size, window_size)
	else: shape = (dataset_size, window_size, window_size, stack.shape[-1])
	dataset = np.zeros(shape, dtype=np.float32)
	labels = np.zeros((dataset_size, num_classes), dtype=np.float32)
	# Transforma o label no formato one-hot
	labels[:,label] = 1.0
	# Extrai janelas centradas nas picks_coords
	i = 0
	for [time_index, trace_index] in picks_coord:
		# Caso pick esteja muito próximo da borda, copia apenas o range apropriado
		data_rmin = max(0, half_size - time_index)
		data_rmax = min(window_size, half_size + stack.shape[0] - time_index)
		data_cmin = max(0, half_size - trace_index) 
		data_cmax = min(window_size, half_size + stack.shape[1] - trace_index)
		tmin = time_index - half_size
		stack_rmin = max(0, tmin)
		stack_rmax = min(tmin + window_size, stack.shape[0])
		tmin = trace_index - half_size
		stack_cmin = max(0, tmin)
		stack_cmax = min(tmin + window_size, stack.shape[1])
		dataset[i,data_rmin:data_rmax,data_cmin:data_cmax] = \
			stack[stack_rmin:stack_rmax, stack_cmin:stack_cmax]
		i += 1

	return dataset, labels


def generate_samples_zoom(stack, window_size, picks_coord, label, num_classes=2, zoom_list = [1]):
	"""Extrai as amostras rotuladas do empilhamento.

	Args:
		stack: empilhamento (numpy.array)
		window_size: tamanho da janela ao redor do pick
		picks_coord: coordenadas da matriz referente ao rótulo
		label: rótulo (eventou ou não evento)
		num_classes: número de classes do problema
		flip: se deve ou não duplicar cada amostra usando espelhamento

	Retorno:
		dataset: conjunto de amostras (janelas) centradas nas picks_coords
		labels: conjunto de rótulos referentes a cada janela, no formato one-hot
	"""
	half_size = window_size // 2 # Divisão inteira
	dataset_size = len(picks_coord)
	zoom_size = len(zoom_list)	
	dataset = np.zeros((zoom_size*dataset_size, window_size, window_size))
	labels = np.zeros((zoom_size*dataset_size, num_classes), dtype=np.float32)
	# Transforma o label no formato one-hot
	labels[:,label] = 1.0
	# Extrai janelas centradas nas picks_coords
	j = 0
	for [time_index, trace_index] in picks_coord:
		for i in zoom_list:
			half_size_zoom = int(i * window_size // 2)
			window_size_zoom = int(i * window_size)
			# Caso pick esteja muito próximo da borda, copia apenas o range apropriado
			data_rmin = max(0, half_size_zoom - time_index)
			data_rmax = min(window_size_zoom, half_size_zoom + stack.shape[0] - time_index)
			data_cmin = max(0, half_size_zoom - trace_index) 
			data_cmax = min(window_size_zoom, half_size_zoom + stack.shape[1] - trace_index)
			tmin = time_index - half_size_zoom
			stack_rmin = max(0, tmin)
			stack_rmax = min(tmin + window_size_zoom, stack.shape[0])
			tmin = trace_index - half_size_zoom
			stack_cmin = max(0, tmin)
			stack_cmax = min(tmin + window_size_zoom, stack.shape[1])
			
			zoom = float(window_size)/float(window_size_zoom)
			data = ndimage.zoom(stack[stack_rmin:stack_rmax, stack_cmin:stack_cmax],zoom, order=0, mode='nearest')
			dataset[j, 0:data.shape[0], 0:data.shape[1]] = data
			j += 1

	return dataset, labels

def prepare_data_for_network(data, window_size, padding='VALID'):
	"""Adiciona (possivelmente) padding no dado. Caso dado não tenha volume, remodela
	para ter volume 1.

	Args:
		data: dado a ser remodelado (numpy.array)
		window_size: tamanho da janela onde será feita a inferência
		padding: borda de zeros a ser inserida. Valores possíveis:
			- 'SAME': adiciona zeros suficentes para que a saída da rede tenha
					mesma dimensão da entrada.
			- 'VALID': sem padding (janela vai deslizar somente pelo dado válido)

	Retorno:
		data: dado remodelado.
	"""
	# Se dado é 2D, adiciona camada de volume
	if (data.shape[-1] != 1): data = data.reshape(data.shape + (1,))
	# Adiciona padding, se necessário
	if padding == 'SAME':
		# Quanto é adicionado em cada dimensão (pensando em um cubo):
		#   ((pad_acima, pad_abaixo),
		#	(pad_esquerda, pad_direita),
		#	(pad_frente, pad_trás))
		half_window = window_size//2
		# Se a janela tiver tamanho par, as bordas direita e inferior devem ter um
		# pixel a menos que as da esquerda e superior
		if window_size % 2 == 0:
			pad = ( (half_window, half_window-1),
					(half_window, half_window-1),
					(0, 0) )
		# Se tiver tamanho ímpar, o padding é o mesmo em todas as bordas
		else:
			pad = ( (half_window, half_window),
					(half_window, half_window),
					(0, 0) )
		data = np.pad(data, pad, mode='constant')
		print("Adicionado borda de zeros de largura", half_window)
	elif padding == 'VALID':
		print("Nenhuma borda adicionada")
	else:
		print("Padding invalido: valores devem ser 'SAME' ou 'VALID'")
		return None
	print("Novo formato do dado:", data.shape)
	return data



def view_seismic_stack(stack_data, apices=None, intersects=None, nonapices=None, 
						cdp_offset=0.0, dt=1.0, 
						resize=1.0, clip_percent=1.0, vmin=None, vmax=None, 
						color='gray', title="", legend_loc=None):
	"""Visualiza o empilhamento

	Args:
		stack_data: matriz (numpy.array) contendo os dados do empilhamento (traços sem o cabeçalho)
		apices: pontos considerados apices. Default: None
		intersects: pontos considerados ápices com intersecção. Default: None
		nonapices: pontos considerados não-ápices. Default: None
		cdp_offset: número do primeiro CDP. Default: 0.0
		dt: valor da amostragem (em segundos). Default: 1.0
		resize: fator de redimensionamento a imagem. Default: 1.0
		clip_percent: trunca a amplitude do empilhamento em 'clip_percent' do valor máximo, para efeitos de
					visualização. Deve ser um número no intervalo [0.0, 1.0]. Default: 1.0
		color: que padrão de cores usar na visualização. Deve ser um cmap válido do matplotlib.
					Default: 'gray'.
		vmin: valor mínimo da escala de cor. É multiplicado pelo fator clip_percent. Default: None
		vmax: valor máximo da escala de cor. É multiplicado pelo fator clip_percent. Default: None
		title: título da imagem. Default: ""

	Retorno:
		Nenhum, somente plota o empilhamento

	Obs:
		Se cdp_offset = 0 e dt = 1, plota a imagem com os índices da matriz
	"""
	# Verifica se o 'clip_percent' é válido
	if not (clip_percent >= 0.0 and clip_percent <= 1.0):
		print("Erro: clip_percent deve ser um numero entre 0.0 e 1.0")
		return

	# Determina tamanho da figura
	fig = plt.figure()
	dpi = float(fig.get_dpi())
	img_width = resize * (stack_data.shape[1] / dpi)
	img_height = resize * (stack_data.shape[0] / dpi)
	fig.set_size_inches(img_width, img_height)
	print("Tamanho da imagem (em polegadas): %.2f x %.2f" % (img_width, img_height))

	# Plota a imagem
	if not vmax is None:
		vmax = vmax * clip_percent
	else:
		vmax = stack_data.max() * clip_percent
	if not vmin is None:
		vmin = vmin * clip_percent
	else:
		vmin = stack_data.min() * clip_percent
	plot_coord = [cdp_offset, stack_data.shape[1] + cdp_offset, stack_data.shape[0] * dt, 0]
	plt.imshow(stack_data, cmap=color, aspect='auto', vmin=vmin, vmax=vmax, extent=plot_coord)
	plt.colorbar()

	# Plota pontos, se houver
	if not apices is None:
		apices_cdp_indices = [cdp for cdp, _ in apices]
		apices_time_indices = [time for _, time in apices]
		plt.scatter(apices_cdp_indices, apices_time_indices, c='g', marker='.', label='apices picks')
	if not intersects is None:
		intersects_cdp_indices = [cdp for cdp, _ in intersects]
		intersects_time_indices = [time for _, time in intersects]
		plt.scatter(intersects_cdp_indices, intersects_time_indices, c='y', marker='.', label='intersects picks')
	if not nonapices is None:
		nonapices_cdp_indices = [cdp for cdp, _ in nonapices]
		nonapices_time_indices = [time for _, time in nonapices]
		plt.scatter(nonapices_cdp_indices, nonapices_time_indices, c='r', marker='.', label='nonapices picks')
	# Ativa a legenda
	if not (apices is None and intersects is None and nonapices is None) and legend_loc:
		plt.legend(loc=legend_loc)

	# Trata eventos de clique
	def onclick(mouse_event):
		button = mouse_event.button
		cdp = mouse_event.xdata
		time = mouse_event.ydata
		if (button == 1 or button == 3):
			event = max(2.0-button, 0.0)
			print('evento=%.1f, cdp=%f, tempo=%f' % (event, cdp, time))
		elif button == 2:
			print("Coord: %d, %d" % (int(cdp), int(time)))	
	cid = fig.canvas.mpl_connect('button_press_event', onclick)

	# Insere nomes e mostra a figura
	plt.xlabel('CMP')
	plt.ylabel('Time (s)')
	if title != "": plt.title(title)
	#plt.tight_layout(pad=pad)
	plt.show()
	return



def event_picker(stack_data, x_begin=0, y_begin=0, x_end=None, y_end=None, 
			cdp_offset=0, dt=1.0, time_scale='s', 
			resize=1.0, clip_percent=1.0, color='gray',
			vmin=None, vmax=None, 
			save_file=None):
	"""Permite realizar picks de eventos numa janela da imagem
			- Botão esquerdo: dá (cdp, tempo) de evento;
			- Botão direito: dá (cdp, tempo) de não-evento;
			- Botão do meio: dá coordenada do ponto

	Args:
		stack_data: matriz (numpy.array) contendo os dados do empilhamento (traços sem o cabeçalho)
		x,y_begin, x,y_end: início e fim da janela
		cdp_offset: número do primeiro CDP
		dt: valor da amostragem (em segundos)
		time_scale: escala temporal dos picks. Pode ser 's' (segundo) ou 'ms' (milissegundo)
					Default: 's'
		resize: fator de redimensionamento a imagem. Default: 1.0
		clip_percent: trunca a amplitude do empilhamento em 'clip_percent' do valor máximo, para efeitos de
					visualização. Deve ser um número no intervalo [0.0, 1.0]. Default: 1.0
		color: que padrão de cores usar na visualização. Deve ser um cmap válido do matplotlib.
					Default: 'gray'.
		vmin, vmax: valores mínimo e máximo para o mapa de cores
		save_file: se diferente de None, dá append dos picks no arquivo indicado.

	Retorno:
		Nenhum, somente plota o empilhamento

	Obs:
		Se cdp_offset = 0 e dt = 1, plota a imagem com os índices da matriz
	"""
	# Verifica se o 'clip_percent' é válido
	if not (clip_percent >= 0.0 and clip_percent <= 1.0):
		print("Erro: clip_percent deve ser um numero entre 0.0 e 1.0")
		return

	# Determina o valor de escala temporal
	if (time_scale=='s'): time_scale = 1.0
	elif (time_scale=='ms'): time_scale = 1.0e3
	else:
		print(time_scale, "nao e uma escala temporal valida. Valores possiveis sao 's' ou 'ms'")
		return

	# Verifica se janela é válida
	if x_end is None: x_end = stack_data.shape[1]
	if y_end is None: y_end = stack_data.shape[0]
	if (x_begin < 0 or y_begin < 0 or\
		x_end > stack_data.shape[1] or y_end > stack_data.shape[0]):
		print("Erro: coordenada da janela fora das dimensoes do empilhamento.")
		return

	# Determina tamanho da figura
	fig = plt.figure()
	dpi = float(fig.get_dpi())
	img_width = resize * ((x_end - x_begin) / dpi)
	img_height = resize * ((y_end - y_begin) / dpi)
	fig.set_size_inches(img_width, img_height)
	print("Tamanho da imagem (em polegadas): %.2f x %.2f" % (img_width, img_height))

	# Plota a imagem
	if not vmax is None:
		vmax = vmax * clip_percent
	else:
		vmax = stack_data.max() * clip_percent
	if not vmin is None:
		vmin = vmin * clip_percent
	else:
		vmin = -vmax
	dt_offset = y_begin * dt
	plot_coord = [x_begin+cdp_offset, x_end + cdp_offset, y_end * dt, dt_offset]
	img = stack_data[y_begin:y_end, x_begin:x_end]
	print("Coordenadas:  x - [%.1f, %.1f], y - [%.1f, %.1f]" % 
		(plot_coord[0], plot_coord[1], plot_coord[3], plot_coord[2]))
	print("Dimensao:", img.shape)
	print("")
	plt.imshow(img, cmap=color, aspect='auto', vmin=vmin, vmax=vmax, extent=plot_coord)
	plt.colorbar()

	# Trata eventos de clique
	def onclick(mouse_event):
		button = mouse_event.button
		cdp = mouse_event.xdata
		time = mouse_event.ydata
		time *= time_scale
		if (button == 1 or button == 3):
			event = max(2.0-button, 0.0)
			event_coord = 'evento=%.1f, cdp=%f, tempo=%f' % (event, cdp, time)
			# Faz append das coordenadas no arquvio save_file, se houver
			if not save_file is None:
				with open(save_file, 'a') as f: f.writelines([event_coord,'\n'])
			print(event_coord)
		elif button == 2:
			print("Coord: %d, %d" % (int(cdp), int(time)))	
	cid = fig.canvas.mpl_connect('button_press_event', onclick)

	# Insere nomes e mostra a figura
	plt.xlabel('CDP')
	plt.ylabel('Tempo (s)')
	plt.show()
	return


def view_samples(dataset, labels, label_names=['',''], label_colors=['r', 'g'],
				num_samples=None, num_columns=5, resize=1.0, color='gray', title="",
				save_fig=None):
	"""Visualiza um conjunto de amostras

	Args:
		dataset: conjunto de amostras
		labels: rótulos das amostras
		label_names: lista com o nome de cada rótulo
		label_colors: lista com a cor de cada rótulo
		num_samples: quantas amostras do dataset deve-se sortear para visualização.
			Se None, visualiza o dataset inteiro
		num_columns: em quantas colunas plotar as amostras
		resize: fator de redimensionamento a imagem. Default: 1.0
		color: que padrão de cores usar na visualização. Deve ser um cmap válido do matplotlib.
					Default: 'gray'.
		title: título da imagem
		save_fig: caminho para salvar a figura como imagem. Se None, mostra a figura
			ao invés de salvá-la.
	
	Retorno:
		Nenhum, somente plota as amostras
	"""
	# Se num_samples estiver especificado, sorteia num_samples amostras 
	if not num_samples is None:
		if num_samples > dataset.shape[0]:
			print("Erro: 'num_samples' deve ser menor ou igual ao tamanho do dataset")
			return
		from sklearn.utils import resample
		dataset, labels = resample(dataset, labels, replace=False, n_samples=num_samples)
	dataset_size = dataset.shape[0]
	half_window = dataset.shape[1] // 2
	num_columns = min(num_columns, dataset_size)
	num_lines = int(np.ceil(float(dataset_size)/num_columns))
	vmax = dataset.max()
	vmin = -vmax 
	print("Visualizando '%s' - %d amostras" % (title, dataset_size))
	# Plota as amostras 
	fig_width = resize * num_columns
	fig_height = resize * num_lines
	fig, axarr = plt.subplots(num_lines, num_columns, figsize=(fig_width, fig_height))
	if title != "":
		sup_title = fig.suptitle(title)
	else: sup_title = None
	for i in range(num_lines):
		for j in range(num_columns):
			index = i*num_columns + j
			if (num_lines > 1): ax = axarr[i, j]
			else: ax = axarr[j]
			ax.axis('off')
			if (index < dataset_size): 
				im = ax.imshow(dataset[index,:,:], cmap=color, vmin=vmin, vmax=vmax)
				label = np.argmax(labels[index])
				img_label = label_names[label] 
				label_color = label_colors[label]
				ax.set_title(img_label)
				# Marca o evento/não-evento no ponto central
				ax.scatter([half_window], [half_window], c=label_color, marker='x')
	fig.tight_layout()
	if not sup_title is None:
		sup_title.set_y(0.95)
		fig.subplots_adjust(top=0.85)	
	if save_fig: 
		plt.savefig(save_fig)
		plt.close(fig)
		print("Figura salva em", save_fig)
	else: plt.show()
	


def inference_to_picks(inference, cdp_offset, dt, threshold=0.5):
	"""Gera coordenadas no formato (CDP, tempo (s)) a partir de um mapa de inferências.

	Args:
		inference: inferencia a ser analisada
		cdp_offset: número do CDP inicial
		dt: intervalo de tempo 
		threshold: limiar acima do qual será considerado que a inferência foi positiva
					(mapeia 'threshold' para 1.0). Default: 0.5

	Retorno:
		Coordenadas do mapa de inferência nas quais o valor foi acima de 'threshold',
		no formato (CDP, tempo (s)).
	"""
	# Cria cópia para não sobrescrever o dado original
	inference = inference.copy()
	# Limiariza a inferencia
	inference[inference >= threshold] = 1.0
	inference[inference < threshold] = 0.0
	# Extrai as coordenadas de cada inferencia
	ind_row, ind_col = np.where(inference == 1.0)
	ind_row = ind_row.astype(np.float32)
	ind_col = ind_col.astype(np.float32)
	# Transforma as coordenadas de linha em índices de tempo
	ind_row *= dt
	# Transforma as coordenadas de coluna em índices CDP
	ind_col += cdp_offset
	# Gera lista de picks no formato (CDP, tempo (s))
	picks = zip(ind_col, ind_row)
	return np.array(picks)




def pickle_data(pickle_file, data_list, name_list):
	"""Salva (pickle) um conjunto de dados para uso futuro.

	Args:
		pickle_file: nome do arquivo onde o dado será salvo
		data_list: lista com os dados a serem salvos
		name_list: lista com o nome de cada dado
	
	Retorno:
		Nenhum, somente salva o dado em disco.

	Obs: data_list e name_list devem ter o mesmo tamanho.
	"""
	if (len(data_list) != len(name_list)):
		print("Erro: lista de dados e lista de nomes devem ter o mesmo tamanho. Nada foi salvo.")
		return
	# Cria diretório para o arquivo, se necessários
	pickle_dir = os.path.dirname(pickle_file)
	if not os.path.exists(pickle_dir): os.mkdir(pickle_dir)
	# Constrói dicionário que associa cada nome a um dado:
	save_dic = {}
	for data, name in zip(data_list, name_list):
		# Sanity check: verifica se não tem nome repetido na lista de nomes
		if save_dic.has_key(name):
			print("Erro - nome duplicado:", name)
			print("Nada foi salvo.")
			return
		save_dic[name] = data
	# Salva o conjunto de dados
	try:
		f = open(pickle_file, 'wb')
		pickle.dump(save_dic, f, pickle.HIGHEST_PROTOCOL)
		f.close()
		print("Dado persistido em", pickle_file)
	except Exception as e:
		print('Erro: nao foi possivel salvar o dado em', pickle_file, ':', e)
		raise



def load_pickle(pickle_file):
	"""Carrega um conjunto de dados preservado em um pickle
	
	Args:
		pickle_file: nome do arquivo que contém os dados.

	Retorno:
		Dicionário com pares { nome do dado : conteúdo }
	"""

	#sys.setdefaultencoding('utf8')
	with open(pickle_file, 'rb') as f:
		data_dic = pickle.load(f)
	print('Dados carregados de', pickle_file)
	for key in data_dic.keys():
		print(" -", key)
	return data_dic


