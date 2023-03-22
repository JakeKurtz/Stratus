# ------------------------------------------------------------------------- #
#
#    Copyright (C) 2023 Jake Kurtz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ------------------------------------------------------------------------- #

import gpu
from gpu_extras.batch import batch_for_shader

from ... import globals

def new_shader(name, vert_shader, frag_shader, coords, indices):
    globals.SHADER[name] = gpu.types.GPUShader(vert_shader, frag_shader, )
    globals.BATCH[name] = batch_for_shader(globals.SHADER[name], 'TRIS', {"position": coords}, indices=indices)

