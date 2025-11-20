import streamlit as st

def fact(n):
  if n == 0 or n == 1:
    return 1
  else:
    return n*fact(n-1)
  
def main():
  st.title("Tính Giai Thừa")
  number = st.number_input(
    "Nhập vào một số:",
    min_value = 0,
    max_value = 200
  )
  if st.button("Tính toán"):
    result = fact(number)
    st.write(f"Giai thừa của {number} là {result}")
if __name__ == "__main__":
  main()
  
