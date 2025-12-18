"""
Tests para DivisorDePrompts
Ejecutar: python test_divisor.py
"""

import sys
sys.path.insert(0, '.')

from __init__ import DivisorDePrompts

def test_node():
    node = DivisorDePrompts()
    
    print("=" * 60)
    print("TEST 1: Entrada vacía")
    print("=" * 60)
    result = node.split_prompts("")
    assert result[-1] == 0, "Count debe ser 0"
    assert all(r == "" for r in result[:-1]), "Todos los outputs deben ser vacíos"
    print("✓ PASS\n")
    
    print("=" * 60)
    print("TEST 2: Un solo prompt (sin líneas vacías)")
    print("=" * 60)
    result = node.split_prompts("portrait photo, cinematic light, 85mm")
    assert result[0] == "portrait photo, cinematic light, 85mm"
    assert result[-1] == 1
    print(f"prompt_01: {result[0]}")
    print(f"count: {result[-1]}")
    print("✓ PASS\n")
    
    print("=" * 60)
    print("TEST 3: Tres prompts separados por líneas vacías")
    print("=" * 60)
    input_text = """Prompt 1: portrait photo, cinematic light, shallow depth of field, 85mm

Prompt 2: product photo on white background, softbox lighting, crisp shadows

Prompt 3: wide landscape shot, golden hour, volumetric fog, ultra detailed"""
    
    result = node.split_prompts(input_text)
    print(f"prompt_01: {result[0]}")
    print(f"prompt_02: {result[1]}")
    print(f"prompt_03: {result[2]}")
    print(f"count: {result[-1]}")
    assert result[-1] == 3
    assert "portrait" in result[0]
    assert "product" in result[1]
    assert "landscape" in result[2]
    print("✓ PASS\n")
    
    print("=" * 60)
    print("TEST 4: Múltiples líneas vacías entre prompts")
    print("=" * 60)
    input_text = """Prompt A



Prompt B


Prompt C"""
    
    result = node.split_prompts(input_text)
    print(f"prompt_01: {result[0]}")
    print(f"prompt_02: {result[1]}")
    print(f"prompt_03: {result[2]}")
    print(f"count: {result[-1]}")
    assert result[-1] == 3
    print("✓ PASS\n")
    
    print("=" * 60)
    print("TEST 5: Prompts con saltos internos (preserve_newlines=True)")
    print("=" * 60)
    input_text = """First line of prompt 1
Second line of prompt 1
Third line of prompt 1

First line of prompt 2
Second line of prompt 2"""
    
    result = node.split_prompts(input_text, preserve_newlines=True)
    print(f"prompt_01:\n{result[0]}")
    print(f"\nprompt_02:\n{result[1]}")
    print(f"\ncount: {result[-1]}")
    assert "\n" in result[0], "Debe preservar newlines internos"
    assert result[-1] == 2
    print("✓ PASS\n")
    
    print("=" * 60)
    print("TEST 6: Prompts con saltos internos (preserve_newlines=False)")
    print("=" * 60)
    result = node.split_prompts(input_text, preserve_newlines=False)
    print(f"prompt_01: {result[0]}")
    print(f"prompt_02: {result[1]}")
    assert "\n" not in result[0], "No debe tener newlines"
    assert "  " not in result[0], "No debe tener espacios dobles"
    print("✓ PASS\n")
    
    print("=" * 60)
    print("TEST 7: Windows newlines (\\r\\n)")
    print("=" * 60)
    input_text = "Prompt Win 1\r\n\r\nPrompt Win 2\r\n\r\nPrompt Win 3"
    result = node.split_prompts(input_text)
    print(f"prompt_01: {result[0]}")
    print(f"prompt_02: {result[1]}")
    print(f"prompt_03: {result[2]}")
    print(f"count: {result[-1]}")
    assert result[-1] == 3
    print("✓ PASS\n")
    
    print("=" * 60)
    print("TEST 8: Más de 10 prompts (debe ignorar el resto)")
    print("=" * 60)
    prompts = [f"Prompt número {i+1}" for i in range(15)]
    input_text = "\n\n".join(prompts)
    result = node.split_prompts(input_text)
    print(f"count: {result[-1]} (de 15 ingresados)")
    assert result[-1] == 10, "Debe limitar a 10"
    assert result[9] == "Prompt número 10"
    print("✓ PASS\n")
    
    print("=" * 60)
    print("TEST 9: Líneas con solo espacios/tabs entre prompts")
    print("=" * 60)
    input_text = "Prompt A\n   \n\t\nPrompt B"
    result = node.split_prompts(input_text)
    print(f"prompt_01: {result[0]}")
    print(f"prompt_02: {result[1]}")
    print(f"count: {result[-1]}")
    assert result[-1] == 2
    print("✓ PASS\n")
    
    print("=" * 60)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 60)

if __name__ == "__main__":
    test_node()
