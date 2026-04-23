#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单片机驱动代码生成器
功能：根据选择的单片机型号、外设接口和代码语言，生成标准驱动初始化代码
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
import datetime

class MCUDriverGenerator:
    def __init__(self, root):
        """初始化应用程序"""
        self.root = root
        self.root.title("单片机驱动代码生成器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置字体
        self.title_font = ("SimHei", 16, "bold")
        self.label_font = ("SimHei", 10)
        self.button_font = ("SimHei", 10)
        self.code_font = ("Consolas", 10)
        
        # 支持的选型列表
        self.mcu_models = [
            "STM32F103", "STM32F407", "STM32H743", 
            "AT89C51", "ESP32", "GD32F103", "HC32L136", "ATSAME70"
        ]
        self.peripherals = [
            "GPIO", "UART", "I2C", "SPI", "CAN", "ADC", "PWM", "TIM"
        ]
        self.languages = ["C语言", "C++语言"]
        
        # 库函数类型映射
        self.lib_types = {
            "STM32F103": ["标准库", "LL库", "HAL库"],
            "STM32F407": ["标准库", "LL库", "HAL库"],
            "STM32H743": ["HAL库", "LL库"],
            "ESP32": ["ESP-IDF库"],
            "GD32F103": ["GD标准库", "HAL库"],
            "HC32L136": ["HC标准库"],
            "AT89C51": ["寄存器操作"],
            "ATSAME70": ["Atmel START库", "ASF库"]
        }
        
        # 默认晶振频率映射
        self.default_xtal = {
            "STM32F103": 16,
            "STM32F407": 16,
            "STM32H743": 16,
            "ESP32": 26,
            "GD32F103": 16,
            "HC32L136": 16,
            "AT89C51": 11.0592,
            "ATSAME70": 16
        }
        
        # 初始化变量
        self.selected_mcu = tk.StringVar()
        self.selected_peripheral = tk.StringVar()
        self.selected_language = tk.StringVar(value="C语言")
        self.selected_lib = tk.StringVar()
        self.xtal_frequency = tk.DoubleVar()

        
        # 外设参数
        self.peripheral_params = {
            "GPIO": {
                "pin": tk.StringVar(value="PA0"),
                "mode": tk.StringVar(value="输出"),
                "level": tk.StringVar(value="低电平"),
                "pull": tk.StringVar(value="无")
            },
            "UART": {
                "baudrate": tk.StringVar(value="9600"),
                "databits": tk.StringVar(value="8位"),
                "parity": tk.StringVar(value="无校验"),
                "stopbits": tk.StringVar(value="1位"),
                "flowcontrol": tk.StringVar(value="关闭"),
                "tx_pin": tk.StringVar(value="PA9"),
                "rx_pin": tk.StringVar(value="PA10")
            },
            "I2C": {
                "i2c_mode": tk.StringVar(value="硬件IIC"),
                "mode": tk.StringVar(value="主模式"),
                "slave_addr": tk.StringVar(value="0x48"),
                "speed": tk.StringVar(value="100kHz"),
                "sda_pin": tk.StringVar(value="PB7"),
                "scl_pin": tk.StringVar(value="PB6")
            },
            "SPI": {
                "mode": tk.StringVar(value="模式0"),
                "speed": tk.StringVar(value="1MHz"),
                "databits": tk.StringVar(value="8位"),
                "cpol": tk.StringVar(value="0"),
                "cpha": tk.StringVar(value="0"),
                "cs_pin": tk.StringVar(value="PA4"),
                "mosi_pin": tk.StringVar(value="PA7"),
                "miso_pin": tk.StringVar(value="PA6"),
                "sck_pin": tk.StringVar(value="PA5")
            },
            "CAN": {
                "baudrate": tk.StringVar(value="500kbps"),
                "filter_mode": tk.StringVar(value="列表模式"),
                "filter_id": tk.StringVar(value="0x00"),
                "rx_pin": tk.StringVar(value="PA11"),
                "tx_pin": tk.StringVar(value="PA12")
            },
            "ADC": {
                "channel": tk.StringVar(value="通道0"),
                "samplerate": tk.StringVar(value="1MHz"),
                "resolution": tk.StringVar(value="12位"),
                "ref_voltage": tk.StringVar(value="3.3V"),
                "pin": tk.StringVar(value="PA0")
            },
            "PWM": {
                "channel": tk.StringVar(value="通道1"),
                "frequency": tk.StringVar(value="1kHz"),
                "duty": tk.StringVar(value="50%"),
                "pin": tk.StringVar(value="PA8")
            },
            "TIM": {
                "timer": tk.StringVar(value="TIM1"),
                "count_mode": tk.StringVar(value="向上计数"),
                "prescaler": tk.StringVar(value="7199"),
                "arr": tk.StringVar(value="9999"),
                "period": tk.StringVar(value="1ms")
            }
        }
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建界面元素
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面元素"""
        # 主框架分为左右两部分
        left_frame = ttk.Frame(self.main_frame, width=400)  # 左侧框架，占1/3
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5, expand=False)
        left_frame.pack_propagate(False)  # 保持宽度
        
        right_frame = ttk.Frame(self.main_frame)  # 右侧框架，占2/3
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5, expand=True)
        
        # 左侧框架内容
        # 标题
        title_label = ttk.Label(
            left_frame, 
            text="单片机驱动代码生成器", 
            font=self.title_font
        )
        title_label.pack(pady=5)
        
        # 选择区域框架 - 使用网格布局
        selection_frame = ttk.Frame(left_frame)
        selection_frame.pack(fill=tk.X, pady=2)
        
        # 第一行：单片机型号和外设接口
        ttk.Label(selection_frame, text="选择单片机型号:", font=self.label_font).grid(row=0, column=0, sticky=tk.W, padx=5, pady=1)
        mcu_combobox = ttk.Combobox(
            selection_frame, 
            textvariable=self.selected_mcu, 
            values=self.mcu_models, 
            state="readonly"
        )
        mcu_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=1)
        
        ttk.Label(selection_frame, text="选择外设接口:", font=self.label_font).grid(row=1, column=0, sticky=tk.W, padx=5, pady=1)
        peripheral_combobox = ttk.Combobox(
            selection_frame, 
            textvariable=self.selected_peripheral, 
            values=self.peripherals, 
            state="readonly"
        )
        peripheral_combobox.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=1)
        
        # 第二行：代码语言和库函数类型
        ttk.Label(selection_frame, text="选择代码语言:", font=self.label_font).grid(row=2, column=0, sticky=tk.W, padx=5, pady=1)
        
        language_frame = ttk.Frame(selection_frame)
        language_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=1)
        c_radio = ttk.Radiobutton(
            language_frame, 
            text="C语言", 
            variable=self.selected_language, 
            value="C语言"
        )
        c_radio.pack(side=tk.LEFT, padx=5)
        
        cpp_radio = ttk.Radiobutton(
            language_frame, 
            text="C++语言", 
            variable=self.selected_language, 
            value="C++语言"
        )
        cpp_radio.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(selection_frame, text="选择库函数类型:", font=self.label_font).grid(row=3, column=0, sticky=tk.W, padx=5, pady=1)
        self.lib_combobox = ttk.Combobox(
            selection_frame, 
            textvariable=self.selected_lib, 
            state="readonly"
        )
        self.lib_combobox.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=1)
        
        # 第三行：外部晶振设置
        ttk.Label(selection_frame, text="外部晶振频率:", font=self.label_font).grid(row=4, column=0, sticky=tk.W, padx=5, pady=1)
        self.xtal_entry = ttk.Entry(selection_frame, textvariable=self.xtal_frequency, width=10)
        self.xtal_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=1)
        ttk.Label(selection_frame, text="MHz", font=self.label_font).grid(row=4, column=2, sticky=tk.W, padx=5, pady=1)
        
        # 设置列权重，使输入框能够扩展
        selection_frame.grid_columnconfigure(1, weight=1)
        
        # 外设参数面板
        self.param_frame = ttk.LabelFrame(left_frame, text="外设参数设置")
        self.param_frame.pack(fill=tk.X, pady=5, expand=False)
        
        # 参数预览窗口
        self.preview_frame = ttk.LabelFrame(left_frame, text="参数预览")
        self.preview_frame.pack(fill=tk.X, pady=5, expand=False)
        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame, 
            height=5, 
            font=self.code_font, 
            wrap=tk.WORD
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态提示区域
        self.status_frame = ttk.Frame(left_frame)
        self.status_frame.pack(fill=tk.X, pady=2)
        self.status_label = ttk.Label(
            self.status_frame, 
            text="", 
            font=self.label_font,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=1)
        
        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        generate_button = ttk.Button(
            button_frame, 
            text="生成代码", 
            command=self.generate_code, 
            style="TButton"
        )
        generate_button.pack(side=tk.LEFT, padx=5, expand=True)
        
        copy_button = ttk.Button(
            button_frame, 
            text="复制代码", 
            command=self.copy_code, 
            style="TButton"
        )
        copy_button.pack(side=tk.LEFT, padx=5, expand=True)
        
        save_button = ttk.Button(
            button_frame, 
            text="保存代码", 
            command=self.save_code, 
            style="TButton"
        )
        save_button.pack(side=tk.LEFT, padx=5, expand=True)
        
        # 右侧框架内容 - 代码显示区域
        code_frame = ttk.LabelFrame(right_frame, text="生成的代码")
        code_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页控件
        notebook = ttk.Notebook(code_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 头文件标签页
        header_tab = ttk.Frame(notebook)
        notebook.add(header_tab, text="头文件 (.h)")
        
        # 创建行号和代码区域的框架
        header_frame = ttk.Frame(header_tab)
        header_frame.pack(fill=tk.BOTH, expand=True)
        
        # 行号显示
        self.header_line_numbers = tk.Text(
            header_frame, 
            width=4, 
            font=self.code_font, 
            bg='#e8e8e8', 
            fg='#888888', 
            relief=tk.FLAT,
            wrap=tk.NONE
        )
        self.header_line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.header_line_numbers.insert(tk.END, "1\n")
        self.header_line_numbers.config(state=tk.DISABLED)
        
        # 代码显示
        self.header_text = scrolledtext.ScrolledText(
            header_frame, 
            font=self.code_font, 
            wrap=tk.WORD,
            bg='#f8f8f8'
        )
        self.header_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 源文件标签页
        source_tab = ttk.Frame(notebook)
        notebook.add(source_tab, text="源文件 (.c/.cpp)")
        
        # 创建行号和代码区域的框架
        source_frame = ttk.Frame(source_tab)
        source_frame.pack(fill=tk.BOTH, expand=True)
        
        # 行号显示
        self.source_line_numbers = tk.Text(
            source_frame, 
            width=4, 
            font=self.code_font, 
            bg='#e8e8e8', 
            fg='#888888', 
            relief=tk.FLAT,
            wrap=tk.NONE
        )
        self.source_line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.source_line_numbers.insert(tk.END, "1\n")
        self.source_line_numbers.config(state=tk.DISABLED)
        
        # 代码显示
        self.source_text = scrolledtext.ScrolledText(
            source_frame, 
            font=self.code_font, 
            wrap=tk.WORD,
            bg='#f8f8f8'
        )
        self.source_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 绑定事件
        mcu_combobox.bind("<<ComboboxSelected>>", self.on_mcu_change)
        peripheral_combobox.bind("<<ComboboxSelected>>", self.on_peripheral_change)
        self.selected_lib.trace_add("write", self.update_preview)
        self.xtal_frequency.trace_add("write", self.update_preview)
        
        # 为所有外设参数添加跟踪
        for peripheral, params in self.peripheral_params.items():
            for param_name, param_var in params.items():
                param_var.trace_add("write", self.update_preview)
        
        # 绑定代码文本框的事件
        self.header_text.bind("<<Modified>>", self.update_line_numbers)
        self.source_text.bind("<<Modified>>", self.update_line_numbers)
        
        # 绑定滚动事件，保持行号与代码同步
        self.header_text.bind("<MouseWheel>", self.sync_scroll)
        self.source_text.bind("<MouseWheel>", self.sync_scroll)
        self.header_text.bind("<Up>", self.sync_scroll)
        self.source_text.bind("<Up>", self.sync_scroll)
        self.header_text.bind("<Down>", self.sync_scroll)
        self.source_text.bind("<Down>", self.sync_scroll)
        
        # 配置样式
        style = ttk.Style()
        style.configure("TButton", font=self.button_font)
    
    def generate_code(self):
        """生成驱动代码"""
        mcu = self.selected_mcu.get()
        peripheral = self.selected_peripheral.get()
        language = self.selected_language.get()
        lib_type = self.selected_lib.get()
        xtal = self.xtal_frequency.get()
        
        if not mcu or not peripheral:
            messagebox.showwarning("警告", "请选择单片机型号和外设接口")
            return
        
        # 清空之前的代码
        self.header_text.delete(1.0, tk.END)
        self.source_text.delete(1.0, tk.END)
        
        # 获取外设参数
        params = {}
        if peripheral in self.peripheral_params:
            for param_name, param_var in self.peripheral_params[peripheral].items():
                # 检查param_var是否有get方法（是否是StringVar对象）
                if hasattr(param_var, 'get'):
                    params[param_name] = param_var.get()
                else:
                    # 如果是字符串，直接使用
                    params[param_name] = param_var
        
        # 根据选择生成代码
        try:
            if mcu.startswith("STM32"):
                header_code, source_code = self.generate_stm32_code(mcu, peripheral, language, lib_type, xtal, params)
            elif mcu == "AT89C51":
                header_code, source_code = self.generate_51_code(peripheral, language, lib_type, xtal, params)
            elif mcu == "ESP32":
                header_code, source_code = self.generate_esp32_code(peripheral, language, lib_type, xtal, params)
            elif mcu == "GD32F103":
                header_code, source_code = self.generate_gd32_code(peripheral, language, params)
            elif mcu == "HC32L136":
                header_code, source_code = self.generate_hc32_code(peripheral, language, params)
            elif mcu == "ATSAME70":
                header_code, source_code = self.generate_same70_code(peripheral, language, lib_type, xtal, params)
            else:
                header_code = "// 暂不支持该单片机型号的代码生成"
                source_code = "// 暂不支持该单片机型号的代码生成"
            
            # 显示生成的代码
            self.header_text.insert(tk.END, header_code)
            self.source_text.insert(tk.END, source_code)
            
            # 更新行号
            self.update_line_numbers(None)
            
            # 简单的语法高亮
            self.highlight_syntax()
            
            # 在状态提示区域显示生成成功信息，添加时间戳
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_label.config(text=f"[{timestamp}] 成功: {mcu} {peripheral} 驱动代码生成成功！", foreground="green")
        except Exception as e:
            # 在状态提示区域显示生成失败信息，添加时间戳
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_msg = f"[{timestamp}] 错误: 代码生成失败：{str(e)}"
            self.status_label.config(text=error_msg, foreground="red")
            # 显示错误信息到代码框
            self.header_text.insert(tk.END, f"// 代码生成失败：{str(e)}")
            self.source_text.insert(tk.END, f"// 代码生成失败：{str(e)}")
    
    def generate_stm32_code(self, mcu, peripheral, language, lib_type, xtal, params):
        """生成STM32系列代码"""
        is_cpp = language == "C++语言"
        header_code = []
        source_code = []
        
        # 头文件内容
        if is_cpp:
            header_code.append("#include <cstdint>")
        else:
            header_code.append("#include <stdint.h>")
        
        # 根据STM32系列和库函数类型选择不同的头文件
        if mcu == "STM32F103":
            if lib_type == "标准库":
                header_code.append('#include "stm32f10x.h"')
            elif lib_type == "HAL库":
                header_code.append('#include "stm32f1xx_hal.h"')
            elif lib_type == "LL库":
                header_code.append('#include "stm32f1xx_ll_gpio.h"')
                if peripheral in ["UART", "I2C", "SPI", "CAN", "ADC", "PWM", "TIM"]:
                    header_code.append('#include "stm32f1xx_ll_' + peripheral.lower() + '.h"')
        elif mcu == "STM32F407":
            if lib_type == "标准库":
                header_code.append('#include "stm32f4xx.h"')
            elif lib_type == "HAL库":
                header_code.append('#include "stm32f4xx_hal.h"')
            elif lib_type == "LL库":
                header_code.append('#include "stm32f4xx_ll_gpio.h"')
                if peripheral in ["UART", "I2C", "SPI", "CAN", "ADC", "PWM", "TIM"]:
                    header_code.append('#include "stm32f4xx_ll_' + peripheral.lower() + '.h"')
        elif mcu == "STM32H743":
            if lib_type == "HAL库":
                header_code.append('#include "stm32h7xx_hal.h"')
            elif lib_type == "LL库":
                header_code.append('#include "stm32h7xx_ll_gpio.h"')
                if peripheral in ["UART", "I2C", "SPI", "CAN", "ADC", "PWM", "TIM"]:
                    header_code.append('#include "stm32h7xx_ll_' + peripheral.lower() + '.h"')
        
        header_code.append("")
        
        # 函数声明
        if is_cpp:
            header_code.append("class " + peripheral + "Driver {")
            header_code.append("public:")
            header_code.append("    /**")
            header_code.append("     * @brief 初始化外设")
            header_code.append("     * @retval None")
            header_code.append("     */")
            header_code.append("    static void init();")
            # 添加外设操作函数声明
            if peripheral == "GPIO":
                header_code.append("    /**")
                header_code.append("     * @brief 设置引脚为高电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void set_high();")
                header_code.append("    /**")
                header_code.append("     * @brief 设置引脚为低电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void set_low();")
                header_code.append("    /**")
                header_code.append("     * @brief 翻转引脚电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void toggle();")
                header_code.append("    /**")
                header_code.append("     * @brief 读取引脚电平")
                header_code.append("     * @retval uint8_t 引脚电平值（0或1）")
                header_code.append("     */")
                header_code.append("    static uint8_t read();")
            elif peripheral == "UART":
                header_code.append("    /**")
                header_code.append("     * @brief 发送一个字节数据")
                header_code.append("     * @param byte 要发送的字节数据")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void send_byte(uint8_t byte);")
                header_code.append("    /**")
                header_code.append("     * @brief 发送字符串")
                header_code.append("     * @param str 要发送的字符串指针")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void send_string(const char* str);")
                header_code.append("    /**")
                header_code.append("     * @brief 接收一个字节数据")
                header_code.append("     * @retval uint8_t 接收到的字节数据")
                header_code.append("     */")
                header_code.append("    static uint8_t receive_byte();")
                header_code.append("    /**")
                header_code.append("     * @brief 接收字符串")
                header_code.append("     * @param buffer 接收缓冲区指针")
                header_code.append("     * @param length 缓冲区长度")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void receive_string(char* buffer, uint16_t length);")
                header_code.append("    /**")
                header_code.append("     * @brief 配置UART中断")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void config_interrupt();")
            elif peripheral == "I2C":
                header_code.append("    /**")
                header_code.append("     * @brief 发送I2C起始信号")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void start();")
                header_code.append("    /**")
                header_code.append("     * @brief 发送I2C停止信号")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void stop();")
                header_code.append("    /**")
                header_code.append("     * @brief 发送I2C应答信号")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void send_ack();")
                header_code.append("    /**")
                header_code.append("     * @brief 发送I2C非应答信号")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void send_nack();")
                header_code.append("    /**")
                header_code.append("     * @brief 读取一个字节数据")
                header_code.append("     * @retval uint8_t 读取到的字节数据")
                header_code.append("     */")
                header_code.append("    static uint8_t read_byte();")
                header_code.append("    /**")
                header_code.append("     * @brief 写入一个字节数据")
                header_code.append("     * @param byte 要写入的字节数据")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void write_byte(uint8_t byte);")
                header_code.append("    /**")
                header_code.append("     * @brief 读取从设备寄存器值")
                header_code.append("     * @param slave_addr 从设备地址")
                header_code.append("     * @param reg_addr 寄存器地址")
                header_code.append("     * @retval uint8_t 读取到的寄存器值")
                header_code.append("     */")
                header_code.append("    static uint8_t read_register(uint8_t slave_addr, uint8_t reg_addr);")
                header_code.append("    /**")
                header_code.append("     * @brief 写入从设备寄存器值")
                header_code.append("     * @param slave_addr 从设备地址")
                header_code.append("     * @param reg_addr 寄存器地址")
                header_code.append("     * @param data 要写入的数据")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data);")
            elif peripheral == "SPI":
                header_code.append("    /**")
                header_code.append("     * @brief 发送一个字节数据")
                header_code.append("     * @param byte 要发送的字节数据")
                header_code.append("     * @retval uint8_t 接收到的字节数据")
                header_code.append("     */")
                header_code.append("    static uint8_t send_byte(uint8_t byte);")
                header_code.append("    /**")
                header_code.append("     * @brief 接收一个字节数据")
                header_code.append("     * @retval uint8_t 接收到的字节数据")
                header_code.append("     */")
                header_code.append("    static uint8_t receive_byte();")
                header_code.append("    /**")
                header_code.append("     * @brief 发送和接收数据")
                header_code.append("     * @param tx_data 发送数据缓冲区指针")
                header_code.append("     * @param rx_data 接收数据缓冲区指针")
                header_code.append("     * @param length 数据长度")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void send_receive_data(uint8_t* tx_data, uint8_t* rx_data, uint16_t length);")
                header_code.append("    /**")
                header_code.append("     * @brief 设置CS引脚状态")
                header_code.append("     * @param state CS引脚状态（0或1）")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void set_cs(uint8_t state);")
            elif peripheral == "CAN":
                header_code.append("    /**")
                header_code.append("     * @brief 发送CAN数据帧")
                header_code.append("     * @param id 帧ID")
                header_code.append("     * @param data 数据缓冲区指针")
                header_code.append("     * @param length 数据长度")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void send_frame(uint32_t id, uint8_t* data, uint8_t length);")
                header_code.append("    /**")
                header_code.append("     * @brief 接收CAN数据帧")
                header_code.append("     * @param id 帧ID指针")
                header_code.append("     * @param data 数据缓冲区指针")
                header_code.append("     * @param length 数据长度指针")
                header_code.append("     * @retval uint8_t 接收状态")
                header_code.append("     */")
                header_code.append("    static uint8_t receive_frame(uint32_t* id, uint8_t* data, uint8_t* length);")
                header_code.append("    /**")
                header_code.append("     * @brief 配置CAN过滤器")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void config_filter();")
                header_code.append("    /**")
                header_code.append("     * @brief 配置CAN中断")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void config_interrupt();")
            elif peripheral == "ADC":
                header_code.append("    /**")
                header_code.append("     * @brief 开始ADC转换")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void start_conversion();")
                header_code.append("    /**")
                header_code.append("     * @brief 读取ADC转换值")
                header_code.append("     * @retval uint16_t ADC转换值")
                header_code.append("     */")
                header_code.append("    static uint16_t read_value();")
                header_code.append("    /**")
                header_code.append("     * @brief 配置ADC中断")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void config_interrupt();")
                header_code.append("    /**")
                header_code.append("     * @brief 将ADC值转换为电压")
                header_code.append("     * @param value ADC转换值")
                header_code.append("     * @retval float 转换后的电压值")
                header_code.append("     */")
                header_code.append("    static float convert_to_voltage(uint16_t value);")
            elif peripheral == "PWM":
                header_code.append("    /**")
                header_code.append("     * @brief 启动PWM输出")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void start();")
                header_code.append("    /**")
                header_code.append("     * @brief 停止PWM输出")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void stop();")
                header_code.append("    /**")
                header_code.append("     * @brief 设置PWM占空比")
                header_code.append("     * @param duty 占空比值")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void set_duty(uint32_t duty);")
                header_code.append("    /**")
                header_code.append("     * @brief 设置PWM频率")
                header_code.append("     * @param frequency 频率值")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void set_frequency(uint32_t frequency);")
            elif peripheral == "TIM":
                header_code.append("    /**")
                header_code.append("     * @brief 启动定时器")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void start();")
                header_code.append("    /**")
                header_code.append("     * @brief 停止定时器")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void stop();")
                header_code.append("    /**")
                header_code.append("     * @brief 配置定时器中断")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void config_interrupt();")
                header_code.append("    /**")
                header_code.append("     * @brief 获取定时器计数值")
                header_code.append("     * @retval uint32_t 定时器计数值")
                header_code.append("     */")
                header_code.append("    static uint32_t get_count();")
                header_code.append("    /**")
                header_code.append("     * @brief 重置定时器计数")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void reset_count();")
            header_code.append("};")
            source_code.append("#include \"" + peripheral.lower() + "_driver.h\"")
            source_code.append("")
            source_code.append("void " + peripheral + "Driver::init() {")
        else:
            header_code.append("/**")
            header_code.append(" * @brief 初始化外设")
            header_code.append(" * @retval None")
            header_code.append(" */")
            header_code.append("void " + peripheral + "_init(void);")
            # 添加外设操作函数声明
            if peripheral == "GPIO":
                header_code.append("/**")
                header_code.append(" * @brief 设置引脚为高电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void GPIO_set_high(void);")
                header_code.append("/**")
                header_code.append(" * @brief 设置引脚为低电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void GPIO_set_low(void);")
                header_code.append("/**")
                header_code.append(" * @brief 翻转引脚电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void GPIO_toggle(void);")
                header_code.append("/**")
                header_code.append(" * @brief 读取引脚电平")
                header_code.append(" * @retval uint8_t 引脚电平值（0或1）")
                header_code.append(" */")
                header_code.append("uint8_t GPIO_read(void);")
            elif peripheral == "UART":
                header_code.append("/**")
                header_code.append(" * @brief 发送一个字节数据")
                header_code.append(" * @param byte 要发送的字节数据")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void UART_send_byte(uint8_t byte);")
                header_code.append("/**")
                header_code.append(" * @brief 发送字符串")
                header_code.append(" * @param str 要发送的字符串指针")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void UART_send_string(const char* str);")
                header_code.append("/**")
                header_code.append(" * @brief 接收一个字节数据")
                header_code.append(" * @retval uint8_t 接收到的字节数据")
                header_code.append(" */")
                header_code.append("uint8_t UART_receive_byte(void);")
                header_code.append("/**")
                header_code.append(" * @brief 接收字符串")
                header_code.append(" * @param buffer 接收缓冲区指针")
                header_code.append(" * @param length 缓冲区长度")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void UART_receive_string(char* buffer, uint16_t length);")
                header_code.append("/**")
                header_code.append(" * @brief 配置UART中断")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void UART_config_interrupt(void);")
            elif peripheral == "I2C":
                header_code.append("/**")
                header_code.append(" * @brief 发送I2C起始信号")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void I2C_start(void);")
                header_code.append("/**")
                header_code.append(" * @brief 发送I2C停止信号")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void I2C_stop(void);")
                header_code.append("/**")
                header_code.append(" * @brief 发送I2C应答信号")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void I2C_send_ack(void);")
                header_code.append("/**")
                header_code.append(" * @brief 发送I2C非应答信号")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void I2C_send_nack(void);")
                header_code.append("/**")
                header_code.append(" * @brief 读取一个字节数据")
                header_code.append(" * @retval uint8_t 读取到的字节数据")
                header_code.append(" */")
                header_code.append("uint8_t I2C_read_byte(void);")
                header_code.append("/**")
                header_code.append(" * @brief 写入一个字节数据")
                header_code.append(" * @param byte 要写入的字节数据")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void I2C_write_byte(uint8_t byte);")
                header_code.append("/**")
                header_code.append(" * @brief 读取从设备寄存器值")
                header_code.append(" * @param slave_addr 从设备地址")
                header_code.append(" * @param reg_addr 寄存器地址")
                header_code.append(" * @retval uint8_t 读取到的寄存器值")
                header_code.append(" */")
                header_code.append("uint8_t I2C_read_register(uint8_t slave_addr, uint8_t reg_addr);")
                header_code.append("/**")
                header_code.append(" * @brief 写入从设备寄存器值")
                header_code.append(" * @param slave_addr 从设备地址")
                header_code.append(" * @param reg_addr 寄存器地址")
                header_code.append(" * @param data 要写入的数据")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void I2C_write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data);")
            elif peripheral == "SPI":
                header_code.append("/**")
                header_code.append(" * @brief 发送一个字节数据")
                header_code.append(" * @param byte 要发送的字节数据")
                header_code.append(" * @retval uint8_t 接收到的字节数据")
                header_code.append(" */")
                header_code.append("uint8_t SPI_send_byte(uint8_t byte);")
                header_code.append("/**")
                header_code.append(" * @brief 接收一个字节数据")
                header_code.append(" * @retval uint8_t 接收到的字节数据")
                header_code.append(" */")
                header_code.append("uint8_t SPI_receive_byte(void);")
                header_code.append("/**")
                header_code.append(" * @brief 发送和接收数据")
                header_code.append(" * @param tx_data 发送数据缓冲区指针")
                header_code.append(" * @param rx_data 接收数据缓冲区指针")
                header_code.append(" * @param length 数据长度")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void SPI_send_receive_data(uint8_t* tx_data, uint8_t* rx_data, uint16_t length);")
                header_code.append("/**")
                header_code.append(" * @brief 设置CS引脚状态")
                header_code.append(" * @param state CS引脚状态（0或1）")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void SPI_set_cs(uint8_t state);")
            elif peripheral == "CAN":
                header_code.append("/**")
                header_code.append(" * @brief 发送CAN数据帧")
                header_code.append(" * @param id 帧ID")
                header_code.append(" * @param data 数据缓冲区指针")
                header_code.append(" * @param length 数据长度")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void CAN_send_frame(uint32_t id, uint8_t* data, uint8_t length);")
                header_code.append("/**")
                header_code.append(" * @brief 接收CAN数据帧")
                header_code.append(" * @param id 帧ID指针")
                header_code.append(" * @param data 数据缓冲区指针")
                header_code.append(" * @param length 数据长度指针")
                header_code.append(" * @retval uint8_t 接收状态")
                header_code.append(" */")
                header_code.append("uint8_t CAN_receive_frame(uint32_t* id, uint8_t* data, uint8_t* length);")
                header_code.append("/**")
                header_code.append(" * @brief 配置CAN过滤器")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void CAN_config_filter(void);")
                header_code.append("/**")
                header_code.append(" * @brief 配置CAN中断")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void CAN_config_interrupt(void);")
            elif peripheral == "ADC":
                header_code.append("/**")
                header_code.append(" * @brief 开始ADC转换")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void ADC_start_conversion(void);")
                header_code.append("/**")
                header_code.append(" * @brief 读取ADC转换值")
                header_code.append(" * @retval uint16_t ADC转换值")
                header_code.append(" */")
                header_code.append("uint16_t ADC_read_value(void);")
                header_code.append("/**")
                header_code.append(" * @brief 配置ADC中断")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void ADC_config_interrupt(void);")
                header_code.append("/**")
                header_code.append(" * @brief 将ADC值转换为电压")
                header_code.append(" * @param value ADC转换值")
                header_code.append(" * @retval float 转换后的电压值")
                header_code.append(" */")
                header_code.append("float ADC_convert_to_voltage(uint16_t value);")
            elif peripheral == "PWM":
                header_code.append("/**")
                header_code.append(" * @brief 启动PWM输出")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void PWM_start(void);")
                header_code.append("/**")
                header_code.append(" * @brief 停止PWM输出")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void PWM_stop(void);")
                header_code.append("/**")
                header_code.append(" * @brief 设置PWM占空比")
                header_code.append(" * @param duty 占空比值")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void PWM_set_duty(uint32_t duty);")
                header_code.append("/**")
                header_code.append(" * @brief 设置PWM频率")
                header_code.append(" * @param frequency 频率值")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void PWM_set_frequency(uint32_t frequency);")
            elif peripheral == "TIM":
                header_code.append("/**")
                header_code.append(" * @brief 启动定时器")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void TIM_start(void);")
                header_code.append("/**")
                header_code.append(" * @brief 停止定时器")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void TIM_stop(void);")
                header_code.append("/**")
                header_code.append(" * @brief 配置定时器中断")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void TIM_config_interrupt(void);")
                header_code.append("/**")
                header_code.append(" * @brief 获取定时器计数值")
                header_code.append(" * @retval uint32_t 定时器计数值")
                header_code.append(" */")
                header_code.append("uint32_t TIM_get_count(void);")
                header_code.append("/**")
                header_code.append(" * @brief 重置定时器计数")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void TIM_reset_count(void);")
            source_code.append("#include \"" + peripheral.lower() + "_driver.h\"")
            source_code.append("")
            source_code.append("/**")
            source_code.append(" * @brief 初始化" + peripheral + "外设")
            source_code.append(" * @retval None")
            source_code.append(" */")
            source_code.append("void " + peripheral + "_init(void) {")
        
        # 使用传入的外设参数
        # params = self.peripheral_params[peripheral]
        
        # 辅助函数：解析引脚
        def parse_pin(pin):
            port = pin[1] if pin[0] == "P" else pin[0]
            pin_num = pin[2:] if pin[0] == "P" else pin[1:]
            return port, pin_num
        
        # 辅助函数：获取端口映射
        def get_port_map():
            return {"A": "GPIOA", "B": "GPIOB", "C": "GPIOC", "D": "GPIOD"}
        
        # 辅助函数：获取引脚映射
        def get_pin_map():
            return {"0": "GPIO_Pin_0", "1": "GPIO_Pin_1", "2": "GPIO_Pin_2", "3": "GPIO_Pin_3", "4": "GPIO_Pin_4", "5": "GPIO_Pin_5", "6": "GPIO_Pin_6", "7": "GPIO_Pin_7", "8": "GPIO_Pin_8", "9": "GPIO_Pin_9", "10": "GPIO_Pin_10", "11": "GPIO_Pin_11", "12": "GPIO_Pin_12", "13": "GPIO_Pin_13", "14": "GPIO_Pin_14", "15": "GPIO_Pin_15"}
        
        # 辅助函数：获取RCC映射
        def get_rcc_map():
            return {"A": "RCC_APB2Periph_GPIOA", "B": "RCC_APB2Periph_GPIOB", "C": "RCC_APB2Periph_GPIOC", "D": "RCC_APB2Periph_GPIOD"}
        
        # 跟踪已使能的端口时钟
        enabled_ports = set()
        # 跟踪已定义的结构体类型
        defined_structs = set()
        
        # 辅助函数：为标准库使能GPIO时钟
        def enable_gpio_clock_std(port):
            if port not in enabled_ports:
                enabled_ports.add(port)
                rcc_map = get_rcc_map()
                return f"    RCC_APB2PeriphClockCmd({rcc_map[port]}, ENABLE);  // 使能{get_port_map()[port]}时钟"
            return None
        
        # 辅助函数：为HAL库使能GPIO时钟
        def enable_gpio_clock_hal(port):
            if port not in enabled_ports:
                enabled_ports.add(port)
                return f"    __HAL_RCC_{get_port_map()[port]}_CLK_ENABLE();  // 使能{get_port_map()[port]}时钟"
            return None
        
        # 辅助函数：为LL库使能GPIO时钟
        def enable_gpio_clock_ll(port):
            if port not in enabled_ports:
                enabled_ports.add(port)
                return f"    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_{port.upper()});  // 使能{get_port_map()[port]}时钟"
            return None
        
        # 辅助函数：添加结构体定义（确保只定义一次）
        def add_struct_def(struct_type, comment):
            if struct_type not in defined_structs:
                defined_structs.add(struct_type)
                return f"    {struct_type};  // {comment}"
            return None
        
        # 辅助函数：添加代码行，自动处理空行
        def add_code_line(line):
            if line:
                source_code.append(line)
        
        # 根据库函数类型生成初始化代码
        if lib_type == "标准库":
            # 标准库初始化代码
            if peripheral == "GPIO":
                pin = params["pin"]
                mode = params["mode"]
                output_level = params["level"]
                pull = params["pull"]
                
                # 解析引脚
                port, pin_num = parse_pin(pin)
                port_map = get_port_map()
                rcc_map = get_rcc_map()
                pin_map = get_pin_map()
                
                mode_map = {"输入": "GPIO_Mode_IN_FLOATING", "输出": "GPIO_Mode_Out_PP"}
                pull_map = {"无": "", "上拉": "GPIO_Mode_IPU", "下拉": "GPIO_Mode_IPD"}
                
                source_code.append("    // GPIO初始化函数")
                add_code_line(add_struct_def("GPIO_InitTypeDef GPIO_InitStruct", "定义GPIO初始化结构体变量"))
                source_code.append("    ")
                source_code.append("    // 使能GPIO时钟")
                add_code_line(enable_gpio_clock_std(port))
                source_code.append("    ")
                source_code.append("    // 配置GPIO引脚参数")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[pin_num]};  // 选择引脚{pin}")
                
                if mode == "输入":
                    if pull != "无":
                        source_code.append(f"    GPIO_InitStruct.GPIO_Mode = {pull_map[pull]};  // 配置为{pull}输入模式")
                    else:
                        source_code.append(f"    GPIO_InitStruct.GPIO_Mode = {mode_map[mode]};  // 配置为浮空输入模式")
                else:
                    source_code.append(f"    GPIO_InitStruct.GPIO_Mode = {mode_map[mode]};  // 配置为推挽输出模式")
                    source_code.append("    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;  // 配置输出速度为50MHz")
                
                source_code.extend([
                    f"    GPIO_Init({port_map[port]}, &GPIO_InitStruct);  // 应用GPIO配置到{port_map[port]}端口",
                    "    ",
                    "    // 设置初始输出电平",
                    f"    {'GPIO_SetBits(' + port_map[port] + ', ' + pin_map[pin_num] + ');  // 设置{pin}引脚初始电平为高电平' if output_level == '高电平' else 'GPIO_ResetBits(' + port_map[port] + ', ' + pin_map[pin_num] + ');  // 设置{pin}引脚初始电平为低电平'}"
                ])
            
            elif peripheral == "UART":
                baudrate = params["baudrate"]
                data_bits = params["databits"]
                parity = params["parity"]
                stop_bits = params["stopbits"]
                flow_control = params["flowcontrol"]
                tx_pin = params["tx_pin"]
                rx_pin = params["rx_pin"]
                
                # 解析引脚
                tx_port, tx_num = parse_pin(tx_pin)
                rx_port, rx_num = parse_pin(rx_pin)
                
                port_map = get_port_map()
                pin_map = get_pin_map()
                
                data_bits_map = {"8位": "USART_WordLength_8b", "9位": "USART_WordLength_9b"}
                parity_map = {"无校验": "USART_Parity_No", "奇校验": "USART_Parity_Odd", "偶校验": "USART_Parity_Even"}
                stop_bits_map = {"1位": "USART_StopBits_1", "0.5位": "USART_StopBits_0_5", "2位": "USART_StopBits_2", "1.5位": "USART_StopBits_1_5"}
                flow_control_map = {"关闭": "USART_HardwareFlowControl_None", "开启": "USART_HardwareFlowControl_RTS_CTS"}
                
                source_code.append("    // UART初始化函数")
                add_code_line(add_struct_def("USART_InitTypeDef USART_InitStruct", "定义UART初始化结构体变量"))
                add_code_line(add_struct_def("GPIO_InitTypeDef GPIO_InitStruct", "定义GPIO初始化结构体变量"))
                source_code.append("    ")
                source_code.append("    // 使能时钟")
                source_code.append("    RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1, ENABLE);  // 使能USART1时钟")
                add_code_line(enable_gpio_clock_std(tx_port))
                add_code_line(enable_gpio_clock_std(rx_port))
                source_code.append("    ")
                source_code.append("    // 配置TX引脚")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[tx_num]};  // 选择{tx_pin}引脚作为TX")
                source_code.append("    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF_PP;  // 配置为复用推挽输出模式")
                source_code.append("    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;  // 配置输出速度为50MHz")
                source_code.append(f"    GPIO_Init({port_map[tx_port]}, &GPIO_InitStruct);  // 应用GPIO配置")
                source_code.append("    ")
                source_code.append("    // 配置RX引脚")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[rx_num]};  // 选择{rx_pin}引脚作为RX")
                source_code.append("    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN_FLOATING;  // 配置为浮空输入模式")
                source_code.append(f"    GPIO_Init({port_map[rx_port]}, &GPIO_InitStruct);  // 应用GPIO配置")
                source_code.append("    ")
                source_code.append("    // 配置UART参数")
                source_code.append(f"    USART_InitStruct.USART_BaudRate = {baudrate};  // 设置波特率为{baudrate}")
                source_code.append(f"    USART_InitStruct.USART_WordLength = {data_bits_map[data_bits]};  // 设置数据位为{data_bits}")
                source_code.append(f"    USART_InitStruct.USART_StopBits = {stop_bits_map[stop_bits]};  // 设置停止位为{stop_bits}")
                source_code.append(f"    USART_InitStruct.USART_Parity = {parity_map[parity]};  // 设置校验位为{parity}")
                source_code.append(f"    USART_InitStruct.USART_HardwareFlowControl = {flow_control_map[flow_control]};  // 设置硬件流控制为{flow_control}")
                source_code.append("    USART_InitStruct.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;  // 使能接收和发送模式")
                source_code.append("    USART_Init(USART1, &USART_InitStruct);  // 应用UART配置")
                source_code.append("    ")
                source_code.append("    // 使能UART")
                source_code.append("    USART_Cmd(USART1, ENABLE);  // 使能USART1外设")
            
            elif peripheral == "I2C":
                scl_pin = params["scl_pin"]
                sda_pin = params["sda_pin"]
                
                # 解析引脚
                scl_port, scl_num = parse_pin(scl_pin)
                sda_port, sda_num = parse_pin(sda_pin)
                
                port_map = get_port_map()
                pin_map = get_pin_map()
                
                source_code.append("    // I2C初始化函数")
                add_code_line(add_struct_def("I2C_InitTypeDef I2C_InitStruct", "定义I2C初始化结构体变量"))
                add_code_line(add_struct_def("GPIO_InitTypeDef GPIO_InitStruct", "定义GPIO初始化结构体变量"))
                source_code.append("    ")
                source_code.append("    // 使能时钟")
                source_code.append("    RCC_APB1PeriphClockCmd(RCC_APB1Periph_I2C1, ENABLE);  // 使能I2C1时钟")
                add_code_line(enable_gpio_clock_std(scl_port))
                add_code_line(enable_gpio_clock_std(sda_port))
                source_code.append("    ")
                source_code.append("    // 配置SCL引脚")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[scl_num]};  // 选择{scl_pin}引脚作为SCL")
                source_code.append("    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF_OD;  // 配置为复用开漏输出模式")
                source_code.append("    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;  // 配置输出速度为50MHz")
                source_code.append(f"    GPIO_Init({port_map[scl_port]}, &GPIO_InitStruct);  // 应用GPIO配置")
                source_code.append("    ")
                source_code.append("    // 配置SDA引脚")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[sda_num]};  // 选择{sda_pin}引脚作为SDA")
                source_code.append("    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF_OD;  // 配置为复用开漏输出模式")
                source_code.append("    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;  // 配置输出速度为50MHz")
                source_code.append(f"    GPIO_Init({port_map[sda_port]}, &GPIO_InitStruct);  // 应用GPIO配置")
                source_code.append("    ")
                source_code.append("    // 配置I2C参数")
                source_code.append("    I2C_DeInit(I2C1);  // 复位I2C1")
                source_code.append("    I2C_InitStruct.I2C_Mode = I2C_Mode_I2C;  // 设置I2C模式为I2C")
                source_code.append("    I2C_InitStruct.I2C_DutyCycle = I2C_DutyCycle_2;  // 设置占空比为2")
                source_code.append("    I2C_InitStruct.I2C_OwnAddress1 = 0x00;  // 设置自身地址为0x00")
                source_code.append("    I2C_InitStruct.I2C_Ack = I2C_Ack_Enable;  // 使能应答")
                source_code.append("    I2C_InitStruct.I2C_AcknowledgedAddress = I2C_AcknowledgedAddress_7bit;  // 设置地址长度为7位")
                source_code.append("    I2C_InitStruct.I2C_ClockSpeed = 100000;  // 设置时钟速度为100kHz")
                source_code.append("    I2C_Init(I2C1, &I2C_InitStruct);  // 应用I2C配置")
                source_code.append("    ")
                source_code.append("    // 使能I2C")
                source_code.append("    I2C_Cmd(I2C1, ENABLE);  // 使能I2C1外设")
            elif peripheral == "SPI":
                sck_pin = params.get("sck_pin", "PA5")
                miso_pin = params.get("miso_pin", "PA6")
                mosi_pin = params.get("mosi_pin", "PA7")
                cs_pin = params.get("cs_pin", "PA4")
                
                # 解析引脚
                sck_port, sck_num = parse_pin(sck_pin)
                miso_port, miso_num = parse_pin(miso_pin)
                mosi_port, mosi_num = parse_pin(mosi_pin)
                cs_port, cs_num = parse_pin(cs_pin)
                
                port_map = get_port_map()
                pin_map = get_pin_map()
                
                source_code.append("    // SPI初始化函数")
                add_code_line(add_struct_def("SPI_InitTypeDef SPI_InitStruct", "定义SPI初始化结构体变量"))
                add_code_line(add_struct_def("GPIO_InitTypeDef GPIO_InitStruct", "定义GPIO初始化结构体变量"))
                source_code.append("    ")
                source_code.append("    // 使能时钟")
                source_code.append("    RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE);  // 使能SPI1时钟")
                add_code_line(enable_gpio_clock_std(sck_port))
                add_code_line(enable_gpio_clock_std(miso_port))
                add_code_line(enable_gpio_clock_std(mosi_port))
                add_code_line(enable_gpio_clock_std(cs_port))
                source_code.append("    ")
                source_code.append("    // 配置SCK引脚")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[sck_num]};  // 选择{sck_pin}引脚作为SCK")
                source_code.append("    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF_PP;  // 配置为复用推挽输出模式")
                source_code.append("    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;  // 配置输出速度为50MHz")
                source_code.append(f"    GPIO_Init({port_map[sck_port]}, &GPIO_InitStruct);  // 应用GPIO配置")
                source_code.append("    ")
                source_code.append("    // 配置MISO引脚")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[miso_num]};  // 选择{miso_pin}引脚作为MISO")
                source_code.append("    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN_FLOATING;  // 配置为浮空输入模式")
                source_code.append(f"    GPIO_Init({port_map[miso_port]}, &GPIO_InitStruct);  // 应用GPIO配置")
                source_code.append("    ")
                source_code.append("    // 配置MOSI引脚")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[mosi_num]};  // 选择{mosi_pin}引脚作为MOSI")
                source_code.append("    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_AF_PP;  // 配置为复用推挽输出模式")
                source_code.append("    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;  // 配置输出速度为50MHz")
                source_code.append(f"    GPIO_Init({port_map[mosi_port]}, &GPIO_InitStruct);  // 应用GPIO配置")
                source_code.append("    ")
                source_code.append("    // 配置CS引脚")
                source_code.append(f"    GPIO_InitStruct.GPIO_Pin = {pin_map[cs_num]};  // 选择{cs_pin}引脚作为CS")
                source_code.append("    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_Out_PP;  // 配置为推挽输出模式")
                source_code.append("    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;  // 配置输出速度为50MHz")
                source_code.append(f"    GPIO_Init({port_map[cs_port]}, &GPIO_InitStruct);  // 应用GPIO配置")
                source_code.append(f"    GPIO_SetBits({port_map[cs_port]}, {pin_map[cs_num]});  // CS初始化为高电平")
                source_code.append("    ")
                source_code.append("    // 配置SPI参数")
                source_code.append("    SPI_DeInit(SPI1);  // 复位SPI1")
                source_code.append("    SPI_InitStruct.SPI_Direction = SPI_Direction_2Lines_FullDuplex;  // 设置为全双工模式")
                source_code.append("    SPI_InitStruct.SPI_Mode = SPI_Mode_Master;  // 设置为主机模式")
                source_code.append("    SPI_InitStruct.SPI_DataSize = SPI_DataSize_8b;  // 设置数据宽度为8位")
                source_code.append("    SPI_InitStruct.SPI_CPOL = SPI_CPOL_High;  // 设置时钟极性为高")
                source_code.append("    SPI_InitStruct.SPI_CPHA = SPI_CPHA_2Edge;  // 设置时钟相位为第二个边沿")
                source_code.append("    SPI_InitStruct.SPI_NSS = SPI_NSS_Soft;  // 使用软件NSS")
                source_code.append("    SPI_InitStruct.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_4;  // 设置波特率预分频为4")
                source_code.append("    SPI_InitStruct.SPI_FirstBit = SPI_FirstBit_MSB;  // 设置高位先发送")
                source_code.append("    SPI_InitStruct.SPI_CRCPolynomial = 7;  // 设置CRC多项式")
                source_code.append("    SPI_Init(SPI1, &SPI_InitStruct);  // 应用SPI配置")
                source_code.append("    ")
                source_code.append("    // 使能SPI")
                source_code.append("    SPI_Cmd(SPI1, ENABLE);  // 使能SPI1外设")
            # 其他外设的标准库初始化代码...
            
        elif lib_type == "HAL库":
            # HAL库初始化代码
            if peripheral == "GPIO":
                pin = params["pin"]
                mode = params["mode"]
                output_level = params["level"]
                pull = params["pull"]
                
                # 解析引脚
                port, pin_num = parse_pin(pin)
                pin_num = int(pin_num)
                port_map = get_port_map()
                
                mode_map = {"输入": "GPIO_MODE_INPUT", "输出": "GPIO_MODE_OUTPUT_PP"}
                pull_map = {"无": "GPIO_NOPULL", "上拉": "GPIO_PULLUP", "下拉": "GPIO_PULLDOWN"}
                
                source_code.extend([
                    "    // GPIO初始化函数",
                    "    GPIO_InitTypeDef GPIO_InitStruct;  // 定义GPIO初始化结构体变量",
                    "    ",
                    "    // 使能GPIO时钟",
                    enable_gpio_clock_hal(port),
                    "    ",
                    "    // 配置GPIO引脚参数",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{pin_num};  // 选择{pin}引脚",
                    f"    GPIO_InitStruct.Mode = {mode_map[mode]};  // 配置为{mode}模式",
                    f"    GPIO_InitStruct.Pull = {pull_map[pull]};  // 配置{pull}电阻",
                ])
                
                if mode == "输出":
                    source_code.append("    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;  // 配置输出速度为中等")
                
                source_code.extend([
                    f"    HAL_GPIO_Init({port_map[port]}, &GPIO_InitStruct);  // 应用GPIO配置到{port_map[port]}端口",
                    "    ",
                    "    // 设置初始输出电平",
                    f"    HAL_GPIO_WritePin({port_map[port]}, GPIO_PIN_{pin_num}, {'GPIO_PIN_SET  // 设置{pin}引脚初始电平为高电平' if output_level == '高电平' else 'GPIO_PIN_RESET  // 设置{pin}引脚初始电平为低电平'});"
                ])
            
            elif peripheral == "UART":
                baudrate = params["baudrate"]
                data_bits = params["databits"]
                parity = params["parity"]
                stop_bits = params["stopbits"]
                flow_control = params["flowcontrol"]
                tx_pin = params["tx_pin"]
                rx_pin = params["rx_pin"]
                
                # 解析引脚
                tx_port, tx_num = parse_pin(tx_pin)
                tx_num = int(tx_num)
                rx_port, rx_num = parse_pin(rx_pin)
                rx_num = int(rx_num)
                
                port_map = get_port_map()
                
                data_bits_map = {"8位": "UART_WORDLENGTH_8B", "9位": "UART_WORDLENGTH_9B"}
                parity_map = {"无校验": "UART_PARITY_NONE", "奇校验": "UART_PARITY_ODD", "偶校验": "UART_PARITY_EVEN"}
                stop_bits_map = {"1位": "UART_STOPBITS_1", "2位": "UART_STOPBITS_2"}
                flow_control_map = {"关闭": "UART_HWCONTROL_NONE", "开启": "UART_HWCONTROL_RTS_CTS"}
                
                source_code.extend([
                    "    // UART初始化",
                    "    UART_HandleTypeDef huart;",
                    "    GPIO_InitTypeDef GPIO_InitStruct;",
                    "    ",
                    "    // 使能时钟",
                    "    __HAL_RCC_USART1_CLK_ENABLE();",
                    enable_gpio_clock_hal(tx_port),
                    enable_gpio_clock_hal(rx_port),
                    "    ",
                    "    // 复用功能初始化",
                    "    // 配置GPIO",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{tx_num}; // TX",
                    "    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;",
                    "    GPIO_InitStruct.Pull = GPIO_NOPULL;",
                    "    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;",
                    "    GPIO_InitStruct.Alternate = GPIO_AF7_USART1;",
                    f"    HAL_GPIO_Init({port_map[tx_port]}, &GPIO_InitStruct);",
                    "    ",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{rx_num}; // RX",
                    "    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;",
                    "    GPIO_InitStruct.Pull = GPIO_NOPULL;",
                    "    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;",
                    "    GPIO_InitStruct.Alternate = GPIO_AF7_USART1;",
                    f"    HAL_GPIO_Init({port_map[rx_port]}, &GPIO_InitStruct);",
                    "    ",
                    "    // 配置UART",
                    "    huart.Instance = USART1;",
                    f"    huart.Init.BaudRate = {baudrate};",
                    f"    huart.Init.WordLength = {data_bits_map[data_bits]};",
                    f"    huart.Init.StopBits = {stop_bits_map[stop_bits]};",
                    f"    huart.Init.Parity = {parity_map[parity]};",
                    f"    huart.Init.Mode = UART_MODE_TX_RX;",
                    f"    huart.Init.HwFlowCtl = {flow_control_map[flow_control]};",
                    "    huart.Init.OverSampling = UART_OVERSAMPLING_16;",
                    "    if (HAL_UART_Init(&huart) != HAL_OK)",
                    "    {",
                    "        // 初始化错误处理",
                    "        while(1);",
                    "    }"
                ])
            
            elif peripheral == "I2C":
                scl_pin = params["scl_pin"]
                sda_pin = params["sda_pin"]
                
                # 解析引脚
                scl_port, scl_num = parse_pin(scl_pin)
                scl_num = int(scl_num)
                sda_port, sda_num = parse_pin(sda_pin)
                sda_num = int(sda_num)
                
                port_map = get_port_map()
                
                source_code.extend([
                    "    // I2C初始化",
                    "    I2C_HandleTypeDef hi2c;",
                    "    GPIO_InitTypeDef GPIO_InitStruct;",
                    "    ",
                    "    // 使能时钟",
                    "    __HAL_RCC_I2C1_CLK_ENABLE();",
                    enable_gpio_clock_hal(scl_port),
                    enable_gpio_clock_hal(sda_port),
                    "    ",
                    "    // 复用功能初始化",
                    "    // 配置SCL引脚",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{scl_num}; // SCL",
                    "    GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;",
                    "    GPIO_InitStruct.Pull = GPIO_PULLUP;",
                    "    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;",
                    "    GPIO_InitStruct.Alternate = GPIO_AF4_I2C1;",
                    f"    HAL_GPIO_Init({port_map[scl_port]}, &GPIO_InitStruct);",
                    "    ",
                    "    // 配置SDA引脚",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{sda_num}; // SDA",
                    "    GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;",
                    "    GPIO_InitStruct.Pull = GPIO_PULLUP;",
                    "    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;",
                    "    GPIO_InitStruct.Alternate = GPIO_AF4_I2C1;",
                    f"    HAL_GPIO_Init({port_map[sda_port]}, &GPIO_InitStruct);",
                    "    ",
                    "    // 配置I2C",
                    "    hi2c.Instance = I2C1;",
                    "    hi2c.Init.ClockSpeed = 100000;",
                    "    hi2c.Init.DutyCycle = I2C_DUTYCYCLE_2;",
                    "    hi2c.Init.OwnAddress1 = 0;",
                    "    hi2c.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;",
                    "    hi2c.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;",
                    "    hi2c.Init.OwnAddress2 = 0;",
                    "    hi2c.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;",
                    "    hi2c.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;",
                    "    if (HAL_I2C_Init(&hi2c) != HAL_OK)",
                    "    {",
                    "        // 初始化错误处理",
                    "        while(1);",
                    "    }"
                ])
            elif peripheral == "SPI":
                sck_pin = params.get("sck_pin", "PA5")
                miso_pin = params.get("miso_pin", "PA6")
                mosi_pin = params.get("mosi_pin", "PA7")
                cs_pin = params.get("cs_pin", "PA4")
                
                # 解析引脚
                sck_port, sck_num = parse_pin(sck_pin)
                sck_num = int(sck_num)
                miso_port, miso_num = parse_pin(miso_pin)
                miso_num = int(miso_num)
                mosi_port, mosi_num = parse_pin(mosi_pin)
                mosi_num = int(mosi_num)
                cs_port, cs_num = parse_pin(cs_pin)
                cs_num = int(cs_num)
                
                port_map = get_port_map()
                
                source_code.extend([
                    "    // SPI初始化",
                    "    SPI_HandleTypeDef hspi;",
                    "    GPIO_InitTypeDef GPIO_InitStruct;",
                    "    ",
                    "    // 使能时钟",
                    "    __HAL_RCC_SPI1_CLK_ENABLE();",
                    enable_gpio_clock_hal(sck_port),
                    enable_gpio_clock_hal(miso_port),
                    enable_gpio_clock_hal(mosi_port),
                    enable_gpio_clock_hal(cs_port),
                    "    ",
                    "    // 配置SCK引脚",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{sck_num}; // SCK",
                    "    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;",
                    "    GPIO_InitStruct.Pull = GPIO_NOPULL;",
                    "    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;",
                    "    GPIO_InitStruct.Alternate = GPIO_AF5_SPI1;",
                    f"    HAL_GPIO_Init({port_map[sck_port]}, &GPIO_InitStruct);",
                    "    ",
                    "    // 配置MISO引脚",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{miso_num}; // MISO",
                    "    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;",
                    "    GPIO_InitStruct.Pull = GPIO_NOPULL;",
                    "    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;",
                    "    GPIO_InitStruct.Alternate = GPIO_AF5_SPI1;",
                    f"    HAL_GPIO_Init({port_map[miso_port]}, &GPIO_InitStruct);",
                    "    ",
                    "    // 配置MOSI引脚",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{mosi_num}; // MOSI",
                    "    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;",
                    "    GPIO_InitStruct.Pull = GPIO_NOPULL;",
                    "    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;",
                    "    GPIO_InitStruct.Alternate = GPIO_AF5_SPI1;",
                    f"    HAL_GPIO_Init({port_map[mosi_port]}, &GPIO_InitStruct);",
                    "    ",
                    "    // 配置CS引脚",
                    f"    GPIO_InitStruct.Pin = GPIO_PIN_{cs_num}; // CS",
                    "    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;",
                    "    GPIO_InitStruct.Pull = GPIO_NOPULL;",
                    "    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;",
                    f"    HAL_GPIO_Init({port_map[cs_port]}, &GPIO_InitStruct);",
                    f"    HAL_GPIO_WritePin({port_map[cs_port]}, GPIO_PIN_{cs_num}, GPIO_PIN_SET); // CS初始化为高电平",
                    "    ",
                    "    // 配置SPI",
                    "    hspi.Instance = SPI1;",
                    "    hspi.Init.Mode = SPI_MODE_MASTER;",
                    "    hspi.Init.Direction = SPI_DIRECTION_2LINES;",
                    "    hspi.Init.DataSize = SPI_DATASIZE_8BIT;",
                    "    hspi.Init.CLKPolarity = SPI_POLARITY_HIGH;",
                    "    hspi.Init.CLKPhase = SPI_PHASE_2EDGE;",
                    "    hspi.Init.NSS = SPI_NSS_SOFT;",
                    "    hspi.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_4;",
                    "    hspi.Init.FirstBit = SPI_FIRSTBIT_MSB;",
                    "    hspi.Init.TIMode = SPI_TIMODE_DISABLE;",
                    "    hspi.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;",
                    "    hspi.Init.CRCPolynomial = 10;",
                    "    if (HAL_SPI_Init(&hspi) != HAL_OK)",
                    "    {",
                    "        // 初始化错误处理",
                    "        while(1);",
                    "    }"
                ])
            # 其他外设的HAL库初始化代码...
            
        elif lib_type == "LL库":
            # LL库初始化代码
            if peripheral == "GPIO":
                pin = params["pin"]
                mode = params["mode"]
                output_level = params["level"]
                pull = params["pull"]
                
                # 解析引脚
                port, pin_num = parse_pin(pin)
                pin_num = int(pin_num)
                port_map = get_port_map()
                
                mode_map = {"输入": "LL_GPIO_MODE_INPUT", "输出": "LL_GPIO_MODE_OUTPUT"}
                pull_map = {"无": "LL_GPIO_PULL_NO", "上拉": "LL_GPIO_PULL_UP", "下拉": "LL_GPIO_PULL_DOWN"}
                
                source_code.extend([
                    "    // GPIO初始化函数",
                    "    ",
                    "    // 使能GPIO时钟",
                    enable_gpio_clock_ll(port),
                    "    ",
                    "    // 配置GPIO引脚参数",
                    f"    LL_GPIO_SetPinMode({port_map[port]}, LL_GPIO_PIN_{pin_num}, {mode_map[mode]});  // 配置{mode}模式",
                    f"    LL_GPIO_SetPinPull({port_map[port]}, LL_GPIO_PIN_{pin_num}, {pull_map[pull]});  // 配置{pull}电阻",
                ])
                
                if mode == "输出":
                    source_code.append(f"    LL_GPIO_SetPinSpeed({port_map[port]}, LL_GPIO_PIN_{pin_num}, LL_GPIO_SPEED_FREQ_MEDIUM);  // 配置输出速度为中等")
                
                source_code.extend([
                    "    ",
                    "    // 设置初始输出电平",
                    f"    {'LL_GPIO_SetOutputPin(' + port_map[port] + ', LL_GPIO_PIN_' + str(pin_num) + ');  // 设置{pin}引脚初始电平为高电平' if output_level == '高电平' else 'LL_GPIO_ResetOutputPin(' + port_map[port] + ', LL_GPIO_PIN_' + str(pin_num) + ');  // 设置{pin}引脚初始电平为低电平'}"
                ])
            
            elif peripheral == "UART":
                baudrate = params["baudrate"]
                data_bits = params["databits"]
                parity = params["parity"]
                stop_bits = params["stopbits"]
                flow_control = params["flowcontrol"]
                tx_pin = params["tx_pin"]
                rx_pin = params["rx_pin"]
                
                # 解析引脚
                tx_port, tx_num = parse_pin(tx_pin)
                tx_num = int(tx_num)
                rx_port, rx_num = parse_pin(rx_pin)
                rx_num = int(rx_num)
                
                port_map = get_port_map()
                
                data_bits_map = {"8位": "LL_USART_DATAWIDTH_8B", "9位": "LL_USART_DATAWIDTH_9B"}
                parity_map = {"无校验": "LL_USART_PARITY_NONE", "奇校验": "LL_USART_PARITY_ODD", "偶校验": "LL_USART_PARITY_EVEN"}
                stop_bits_map = {"1位": "LL_USART_STOPBITS_1", "2位": "LL_USART_STOPBITS_2"}
                
                source_code.extend([
                    "    // UART初始化函数",
                    "    GPIO_InitTypeDef GPIO_InitStruct;  // 定义GPIO初始化结构体变量",
                    "    ",
                    "    // 使能时钟",
                    "    LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_USART1);  // 使能USART1时钟",
                    enable_gpio_clock_ll(tx_port),
                    enable_gpio_clock_ll(rx_port),
                    "    ",
                    "    // 配置TX引脚",
                    f"    LL_GPIO_SetPinMode({port_map[tx_port]}, LL_GPIO_PIN_{tx_num}, LL_GPIO_MODE_ALTERNATE);  // 配置为复用模式",
                    f"    LL_GPIO_SetPinSpeed({port_map[tx_port]}, LL_GPIO_PIN_{tx_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                    f"    LL_GPIO_SetPinPull({port_map[tx_port]}, LL_GPIO_PIN_{tx_num}, LL_GPIO_PULL_UP);  // 配置上拉电阻",
                    f"    LL_GPIO_SetAFPin_8_15({port_map[tx_port]}, LL_GPIO_PIN_{tx_num}, LL_GPIO_AF_7);  // 配置为USART1_TX功能",
                    "    ",
                    "    // 配置RX引脚",
                    f"    LL_GPIO_SetPinMode({port_map[rx_port]}, LL_GPIO_PIN_{rx_num}, LL_GPIO_MODE_ALTERNATE);  // 配置为复用模式",
                    f"    LL_GPIO_SetPinSpeed({port_map[rx_port]}, LL_GPIO_PIN_{rx_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                    f"    LL_GPIO_SetPinPull({port_map[rx_port]}, LL_GPIO_PIN_{rx_num}, LL_GPIO_PULL_UP);  // 配置上拉电阻",
                    f"    LL_GPIO_SetAFPin_8_15({port_map[rx_port]}, LL_GPIO_PIN_{rx_num}, LL_GPIO_AF_7);  // 配置为USART1_RX功能",
                    "    ",
                    "    // 配置UART参数",
                    "    LL_USART_DeInit(USART1);  // 复位USART1",
                    f"    LL_USART_SetBaudRate(USART1, SystemCoreClock, LL_USART_OVERSAMPLING_16, {baudrate});  // 设置波特率为{baudrate}",
                    f"    LL_USART_SetDataWidth(USART1, {data_bits_map[data_bits]});  // 设置数据位为{data_bits}",
                    f"    LL_USART_SetStopBitsLength(USART1, {stop_bits_map[stop_bits]});  // 设置停止位为{stop_bits}",
                    f"    LL_USART_SetParity(USART1, {parity_map[parity]});  // 设置校验位为{parity}",
                    "    LL_USART_SetTransferDirection(USART1, LL_USART_DIRECTION_TX_RX);  // 使能接收和发送模式",
                    "    LL_USART_SetHardwareFlowControl(USART1, LL_USART_HWCONTROL_NONE);  // 禁用硬件流控制",
                    "    ",
                    "    // 使能UART",
                    "    LL_USART_Enable(USART1);  // 使能USART1",
                    "    while (!LL_USART_IsActiveFlag_TEACK(USART1) || !LL_USART_IsActiveFlag_REACK(USART1));  // 等待发送和接收确认"
                ])
            
            elif peripheral == "I2C":
                i2c_mode = params.get("i2c_mode", "硬件IIC")
                scl_pin = params["scl_pin"]
                sda_pin = params["sda_pin"]
                
                # 解析引脚
                scl_port, scl_num = parse_pin(scl_pin)
                scl_num = int(scl_num)
                sda_port, sda_num = parse_pin(sda_pin)
                sda_num = int(sda_num)
                
                port_map = get_port_map()
                
                if i2c_mode == "硬件IIC":
                    source_code.extend([
                        "    // I2C初始化函数 - 硬件IIC",
                        "    GPIO_InitTypeDef GPIO_InitStruct;  // 定义GPIO初始化结构体变量",
                        "    ",
                        "    // 使能时钟",
                        "    LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_I2C1);  // 使能I2C1时钟",
                        enable_gpio_clock_ll(scl_port),
                        enable_gpio_clock_ll(sda_port),
                        "    ",
                        "    // 配置SCL引脚",
                        f"    LL_GPIO_SetPinMode({port_map[scl_port]}, LL_GPIO_PIN_{scl_num}, LL_GPIO_MODE_ALTERNATE);  // 配置为复用模式",
                        f"    LL_GPIO_SetPinSpeed({port_map[scl_port]}, LL_GPIO_PIN_{scl_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                        f"    LL_GPIO_SetPinPull({port_map[scl_port]}, LL_GPIO_PIN_{scl_num}, LL_GPIO_PULL_UP);  // 配置上拉电阻",
                        f"    LL_GPIO_SetAFPin_0_7({port_map[scl_port]}, LL_GPIO_PIN_{scl_num}, LL_GPIO_AF_4);  // 配置为I2C1_SCL功能",
                        "    ",
                        "    // 配置SDA引脚",
                        f"    LL_GPIO_SetPinMode({port_map[sda_port]}, LL_GPIO_PIN_{sda_num}, LL_GPIO_MODE_ALTERNATE);  // 配置为复用模式",
                        f"    LL_GPIO_SetPinSpeed({port_map[sda_port]}, LL_GPIO_PIN_{sda_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                        f"    LL_GPIO_SetPinPull({port_map[sda_port]}, LL_GPIO_PIN_{sda_num}, LL_GPIO_PULL_UP);  // 配置上拉电阻",
                        f"    LL_GPIO_SetAFPin_0_7({port_map[sda_port]}, LL_GPIO_PIN_{sda_num}, LL_GPIO_AF_4);  // 配置为I2C1_SDA功能",
                        "    ",
                        "    // 配置I2C参数",
                        "    LL_I2C_DeInit(I2C1);  // 复位I2C1",
                        "    LL_I2C_DisableClockStretching(I2C1);  // 禁用时钟拉伸",
                        "    LL_I2C_SetTiming(I2C1, 0x00901D2B);  // 设置I2C时序参数，100kHz",
                        "    LL_I2C_EnableAutoEndMode(I2C1);  // 使能自动结束模式",
                        "    LL_I2C_SetOwnAddress1(I2C1, 0x00, LL_I2C_ADDRESSING_MODE_7BIT);  // 设置自身地址为0x00，7位地址模式",
                        "    LL_I2C_EnableOwnAddress1(I2C1);  // 使能自身地址1",
                        "    LL_I2C_SetMasterAddressingMode(I2C1, LL_I2C_ADDRESSING_MODE_7BIT);  // 设置主机寻址模式为7位",
                        "    ",
                        "    // 使能I2C",
                        "    LL_I2C_Enable(I2C1);  // 使能I2C1",
                        "    while (!LL_I2C_IsActiveFlag_BUSY(I2C1));  // 等待I2C总线就绪"
                    ])
                else:  # 软件模拟IIC
                    source_code.extend([
                        "    // I2C初始化函数 - 软件模拟IIC",
                        "    GPIO_InitTypeDef GPIO_InitStruct;  // 定义GPIO初始化结构体变量",
                        "    ",
                        "    // 使能时钟",
                        enable_gpio_clock_ll(scl_port),
                        enable_gpio_clock_ll(sda_port),
                        "    ",
                        "    // 配置SCL引脚",
                        f"    LL_GPIO_SetPinMode({port_map[scl_port]}, LL_GPIO_PIN_{scl_num}, LL_GPIO_MODE_OUTPUT);  // 配置为输出模式",
                        f"    LL_GPIO_SetPinSpeed({port_map[scl_port]}, LL_GPIO_PIN_{scl_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                        f"    LL_GPIO_SetPinPull({port_map[scl_port]}, LL_GPIO_PIN_{scl_num}, LL_GPIO_PULL_UP);  // 配置上拉电阻",
                        f"    LL_GPIO_SetOutputPin({port_map[scl_port]}, LL_GPIO_PIN_{scl_num});  // 初始化为高电平",
                        "    ",
                        "    // 配置SDA引脚",
                        f"    LL_GPIO_SetPinMode({port_map[sda_port]}, LL_GPIO_PIN_{sda_num}, LL_GPIO_MODE_OUTPUT);  // 配置为输出模式",
                        f"    LL_GPIO_SetPinSpeed({port_map[sda_port]}, LL_GPIO_PIN_{sda_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                        f"    LL_GPIO_SetPinPull({port_map[sda_port]}, LL_GPIO_PIN_{sda_num}, LL_GPIO_PULL_UP);  // 配置上拉电阻",
                        f"    LL_GPIO_SetOutputPin({port_map[sda_port]}, LL_GPIO_PIN_{sda_num});  // 初始化为高电平"
                    ])
            elif peripheral == "SPI":
                sck_pin = params.get("sck_pin", "PA5")
                miso_pin = params.get("miso_pin", "PA6")
                mosi_pin = params.get("mosi_pin", "PA7")
                cs_pin = params.get("cs_pin", "PA4")
                
                # 解析引脚
                sck_port, sck_num = parse_pin(sck_pin)
                sck_num = int(sck_num)
                miso_port, miso_num = parse_pin(miso_pin)
                miso_num = int(miso_num)
                mosi_port, mosi_num = parse_pin(mosi_pin)
                mosi_num = int(mosi_num)
                cs_port, cs_num = parse_pin(cs_pin)
                cs_num = int(cs_num)
                
                port_map = get_port_map()
                
                source_code.extend([
                    "    // SPI初始化函数",
                    "    GPIO_InitTypeDef GPIO_InitStruct;  // 定义GPIO初始化结构体变量",
                    "    ",
                    "    // 使能时钟",
                    "    LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_SPI1);  // 使能SPI1时钟",
                    enable_gpio_clock_ll(sck_port),
                    enable_gpio_clock_ll(miso_port),
                    enable_gpio_clock_ll(mosi_port),
                    enable_gpio_clock_ll(cs_port),
                    "    ",
                    "    // 配置SCK引脚",
                    f"    LL_GPIO_SetPinMode({port_map[sck_port]}, LL_GPIO_PIN_{sck_num}, LL_GPIO_MODE_ALTERNATE);  // 配置为复用模式",
                    f"    LL_GPIO_SetPinSpeed({port_map[sck_port]}, LL_GPIO_PIN_{sck_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                    f"    LL_GPIO_SetPinPull({port_map[sck_port]}, LL_GPIO_PIN_{sck_num}, LL_GPIO_PULL_NO);  // 配置无拉电阻",
                    f"    LL_GPIO_SetAFPin_0_7({port_map[sck_port]}, LL_GPIO_PIN_{sck_num}, LL_GPIO_AF_5);  // 配置为SPI1_SCK功能",
                    "    ",
                    "    // 配置MISO引脚",
                    f"    LL_GPIO_SetPinMode({port_map[miso_port]}, LL_GPIO_PIN_{miso_num}, LL_GPIO_MODE_ALTERNATE);  // 配置为复用模式",
                    f"    LL_GPIO_SetPinSpeed({port_map[miso_port]}, LL_GPIO_PIN_{miso_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                    f"    LL_GPIO_SetPinPull({port_map[miso_port]}, LL_GPIO_PIN_{miso_num}, LL_GPIO_PULL_NO);  // 配置无拉电阻",
                    f"    LL_GPIO_SetAFPin_0_7({port_map[miso_port]}, LL_GPIO_PIN_{miso_num}, LL_GPIO_AF_5);  // 配置为SPI1_MISO功能",
                    "    ",
                    "    // 配置MOSI引脚",
                    f"    LL_GPIO_SetPinMode({port_map[mosi_port]}, LL_GPIO_PIN_{mosi_num}, LL_GPIO_MODE_ALTERNATE);  // 配置为复用模式",
                    f"    LL_GPIO_SetPinSpeed({port_map[mosi_port]}, LL_GPIO_PIN_{mosi_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                    f"    LL_GPIO_SetPinPull({port_map[mosi_port]}, LL_GPIO_PIN_{mosi_num}, LL_GPIO_PULL_NO);  // 配置无拉电阻",
                    f"    LL_GPIO_SetAFPin_0_7({port_map[mosi_port]}, LL_GPIO_PIN_{mosi_num}, LL_GPIO_AF_5);  // 配置为SPI1_MOSI功能",
                    "    ",
                    "    // 配置CS引脚",
                    f"    LL_GPIO_SetPinMode({port_map[cs_port]}, LL_GPIO_PIN_{cs_num}, LL_GPIO_MODE_OUTPUT);  // 配置为输出模式",
                    f"    LL_GPIO_SetPinSpeed({port_map[cs_port]}, LL_GPIO_PIN_{cs_num}, LL_GPIO_SPEED_FREQ_HIGH);  // 配置输出速度为高速",
                    f"    LL_GPIO_SetPinPull({port_map[cs_port]}, LL_GPIO_PIN_{cs_num}, LL_GPIO_PULL_NO);  // 配置无拉电阻",
                    f"    LL_GPIO_SetOutputPin({port_map[cs_port]}, LL_GPIO_PIN_{cs_num});  // CS初始化为高电平",
                    "    ",
                    "    // 配置SPI参数",
                    "    LL_SPI_DeInit(SPI1);  // 复位SPI1",
                    "    LL_SPI_SetMode(SPI1, LL_SPI_MODE_MASTER);  // 设置为主机模式",
                    "    LL_SPI_SetTransferDirection(SPI1, LL_SPI_FULL_DUPLEX);  // 设置为全双工模式",
                    "    LL_SPI_SetDataWidth(SPI1, LL_SPI_DATAWIDTH_8BIT);  // 设置数据宽度为8位",
                    "    LL_SPI_SetClockPolarity(SPI1, LL_SPI_POLARITY_HIGH);  // 设置时钟极性为高",
                    "    LL_SPI_SetClockPhase(SPI1, LL_SPI_PHASE_2EDGE);  // 设置时钟相位为第二个边沿",
                    "    LL_SPI_SetNSSMode(SPI1, LL_SPI_NSS_SOFT);  // 使用软件NSS",
                    "    LL_SPI_SetBaudRatePrescaler(SPI1, LL_SPI_BAUDRATEPRESCALER_4);  // 设置波特率预分频为4",
                    "    LL_SPI_SetBitOrder(SPI1, LL_SPI_MSB_FIRST);  // 设置高位先发送",
                    "    LL_SPI_DisableCRC(SPI1);  // 禁用CRC",
                    "    ",
                    "    // 使能SPI",
                    "    LL_SPI_Enable(SPI1);  // 使能SPI1",
                    "    while (!LL_SPI_IsActiveFlag_TXE(SPI1));  // 等待发送缓冲区为空"
                ])
            
        source_code.append("}")
        source_code.append("")
        
        # 添加外设操作函数实现
        if is_cpp:
            if peripheral == "GPIO":
                pin = params["pin"]
                # 解析引脚
                port = pin[1] if pin[0] == "P" else pin[0]
                pin_num = int(pin[2:] if pin[0] == "P" else pin[1:])
                port_map = {"A": "GPIOA", "B": "GPIOB", "C": "GPIOC", "D": "GPIOD"}
                
                source_code.extend([
                    "/**",
                    " * @brief 设置引脚为高电平",
                    " * @retval None",
                    " */",
                    f"void GPIO_driver::set_high() {{",
                    "    // 设置引脚高电平",
                    f"    {port_map[port]}->BSRR = GPIO_Pin_{pin_num};",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚为低电平",
                    " * @retval None",
                    " */",
                    f"void GPIO_driver::set_low() {{",
                    "    // 设置引脚低电平",
                    f"    {port_map[port]}->BRR = GPIO_Pin_{pin_num};",
                    "}",
                    "",
                    "/**",
                    " * @brief 翻转引脚电平",
                    " * @retval None",
                    " */",
                    f"void GPIO_driver::toggle() {{",
                    "    // 翻转引脚电平",
                    f"    {port_map[port]}->ODR ^= GPIO_Pin_{pin_num};",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取引脚电平",
                    " * @retval uint8_t 引脚电平值（0或1）",
                    " */",
                    f"uint8_t GPIO_driver::read() {{",
                    "    // 读取引脚电平",
                    f"    return GPIO_ReadInputDataBit({port_map[port]}, GPIO_Pin_{pin_num});",
                    "}"
                ])
            elif peripheral == "UART":
                source_code.extend([
                    "/**",
                    " * @brief 发送一个字节数据",
                    " * @param byte 要发送的字节数据",
                    " * @retval None",
                    " */",
                    "void UARTDriver::send_byte(uint8_t byte) {",
                    "    // 发送一个字节",
                    "    while (!LL_USART_IsActiveFlag_TXE(USART1));",
                    "    LL_USART_TransmitData8(USART1, byte);",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送字符串",
                    " * @param str 要发送的字符串指针",
                    " * @retval None",
                    " */",
                    "void UARTDriver::send_string(const char* str) {",
                    "    // 发送字符串",
                    "    while (*str) {",
                    "        send_byte(*str++);",
                    "    }",
                    "}",
                    "",
                    "/**",
                    " * @brief 接收一个字节数据",
                    " * @retval uint8_t 接收到的字节数据",
                    " */",
                    "uint8_t UARTDriver::receive_byte() {",
                    "    // 接收一个字节",
                    "    while (!LL_USART_IsActiveFlag_RXNE(USART1));",
                    "    return LL_USART_ReceiveData8(USART1);",
                    "}",
                    "",
                    "/**",
                    " * @brief 接收字符串",
                    " * @param buffer 接收缓冲区指针",
                    " * @param length 缓冲区长度",
                    " * @retval None",
                    " */",
                    "void UARTDriver::receive_string(char* buffer, uint16_t length) {",
                    "    // 接收字符串",
                    "    uint16_t i = 0;",
                    "    while (i < length - 1) {",
                    "        buffer[i] = receive_byte();",
                    "        if (buffer[i] == '\\0') break;",
                    "        i++;",
                    "    }",
                    "    buffer[i] = '\\0';",
                    "}",
                    "",
                    "/**",
                    " * @brief 配置UART中断",
                    " * @retval None",
                    " */",
                    "void UARTDriver::config_interrupt() {",
                    "    // 配置UART中断",
                    "    LL_USART_EnableIT_RXNE(USART1);",
                    "    NVIC_EnableIRQ(USART1_IRQn);",
                    "}"
                ])
            elif peripheral == "I2C":
                i2c_mode = params.get("i2c_mode", "硬件IIC")
                scl_pin = params["scl_pin"]
                sda_pin = params["sda_pin"]
                
                # 解析引脚
                scl_port = scl_pin[1] if scl_pin[0] == 'P' else scl_pin[0]
                scl_num = int(scl_pin[2:] if scl_pin[0] == 'P' else scl_pin[1:])
                sda_port = sda_pin[1] if sda_pin[0] == 'P' else sda_pin[0]
                sda_num = int(sda_pin[2:] if sda_pin[0] == 'P' else sda_pin[1:])
                
                port_map = {"A": "GPIOA", "B": "GPIOB", "C": "GPIOC", "D": "GPIOD"}
                
                if i2c_mode == "硬件IIC":
                    source_code.extend([
                        "",
                        "/**",
                        " * @brief 发送I2C起始信号",
                        " * @retval None",
                        " */",
                        "void I2CDriver::start() {",
                        "    // 发送I2C起始信号",
                        "    I2C_GenerateSTART(I2C1, ENABLE);",
                        "    while (!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_MODE_SELECT));",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C停止信号",
                        " * @retval None",
                        " */",
                        "void I2CDriver::stop() {",
                        "    // 发送I2C停止信号",
                        "    I2C_GenerateSTOP(I2C1, ENABLE);",
                        "    while (I2C_GetFlagStatus(I2C1, I2C_FLAG_STOPF));",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C应答信号",
                        " * @retval None",
                        " */",
                        "void I2CDriver::send_ack() {",
                        "    // 发送I2C应答信号",
                        "    I2C_AcknowledgeConfig(I2C1, ENABLE);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C非应答信号",
                        " * @retval None",
                        " */",
                        "void I2CDriver::send_nack() {",
                        "    // 发送I2C非应答信号",
                        "    I2C_AcknowledgeConfig(I2C1, DISABLE);",
                        "}",
                        "",
                        "/**",
                        " * @brief 读取一个字节数据",
                        " * @retval uint8_t 读取到的字节数据",
                        " */",
                        "uint8_t I2CDriver::read_byte() {",
                        "    // 读取一个字节数据",
                        "    while (!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_RECEIVED));",
                        "    return I2C_ReceiveData(I2C1);",
                        "}",
                        "",
                        "/**",
                        " * @brief 写入一个字节数据",
                        " * @param byte 要写入的字节数据",
                        " * @retval None",
                        " */",
                        "void I2CDriver::write_byte(uint8_t byte) {",
                        "    // 写入一个字节数据",
                        "    I2C_SendData(I2C1, byte);",
                        "    while (!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_TRANSMITTED));",
                        "}",
                        "",
                        "/**",
                        " * @brief 读取从设备寄存器值",
                        " * @param slave_addr 从设备地址",
                        " * @param reg_addr 寄存器地址",
                        " * @retval uint8_t 读取到的寄存器值",
                        " */",
                        "uint8_t I2CDriver::read_register(uint8_t slave_addr, uint8_t reg_addr) {",
                        "    // 读取从设备寄存器值",
                        "    start();",
                        "    write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                        "    write_byte(reg_addr); // 发送寄存器地址",
                        "    start(); // 重复起始信号",
                        "    write_byte((slave_addr << 1) | 1); // 发送从设备地址，读模式",
                        "    send_nack(); // 发送非应答",
                        "    uint8_t data = read_byte();",
                        "    stop();",
                        "    return data;",
                        "}",
                        "",
                        "/**",
                        " * @brief 写入从设备寄存器值",
                        " * @param slave_addr 从设备地址",
                        " * @param reg_addr 寄存器地址",
                        " * @param data 要写入的数据",
                        " * @retval None",
                        " */",
                        "void I2CDriver::write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                        "    // 写入从设备寄存器值",
                        "    start();",
                        "    write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                        "    write_byte(reg_addr); // 发送寄存器地址",
                        "    write_byte(data); // 发送数据",
                        "    stop();",
                        "}"
                    ])
                else:  # 软件模拟IIC
                    source_code.extend([
                        "",
                        "// 延时函数",
                        "void I2C_delay(uint32_t us) {",
                        "    uint32_t i = us * 8; // 简单延时",
                        "    while (i--);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C起始信号",
                        " * @retval None",
                        " */",
                        "void I2CDriver::start() {",
                        "    // 发送I2C起始信号",
                        "    LL_GPIO_SetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 1",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 0",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C停止信号",
                        " * @retval None",
                        " */",
                        "void I2CDriver::stop() {",
                        "    // 发送I2C停止信号",
                        "    LL_GPIO_ResetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 0",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_SetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 1",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C应答信号",
                        " * @retval None",
                        " */",
                        "void I2CDriver::send_ack() {",
                        "    // 发送I2C应答信号",
                        "    LL_GPIO_ResetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 0",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C非应答信号",
                        " * @retval None",
                        " */",
                        "void I2CDriver::send_nack() {",
                        "    // 发送I2C非应答信号",
                        "    LL_GPIO_SetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 1",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 读取一个字节数据",
                        " * @retval uint8_t 读取到的字节数据",
                        " */",
                        "uint8_t I2CDriver::read_byte() {",
                        "    // 读取一个字节数据",
                        "    uint8_t data = 0;",
                        "    LL_GPIO_SetPinMode(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ", LL_GPIO_MODE_INPUT);  // SDA = 输入",
                        "    for (int i = 7; i >= 0; i--) {",
                        "        LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "        I2C_delay(5);",
                        "        if (LL_GPIO_IsInputPinSet(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ")) {",
                        "            data |= (1 << i);",
                        "        }",
                        "        LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "        I2C_delay(5);",
                        "    }",
                        "    LL_GPIO_SetPinMode(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ", LL_GPIO_MODE_OUTPUT);  // SDA = 输出",
                        "    return data;",
                        "}",
                        "",
                        "/**",
                        " * @brief 写入一个字节数据",
                        " * @param byte 要写入的字节数据",
                        " * @retval None",
                        " */",
                        "void I2CDriver::write_byte(uint8_t byte) {",
                        "    // 写入一个字节数据",
                        "    for (int i = 7; i >= 0; i--) {",
                        "        if (byte & (1 << i)) {",
                        "            LL_GPIO_SetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 1",
                        "        } else {",
                        "            LL_GPIO_ResetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 0",
                        "        }",
                        "        I2C_delay(5);",
                        "        LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "        I2C_delay(5);",
                        "        LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "        I2C_delay(5);",
                        "    }",
                        "    // 等待应答",
                        "    LL_GPIO_SetPinMode(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ", LL_GPIO_MODE_INPUT);  // SDA = 输入",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "    LL_GPIO_SetPinMode(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ", LL_GPIO_MODE_OUTPUT);  // SDA = 输出",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 读取从设备寄存器值",
                        " * @param slave_addr 从设备地址",
                        " * @param reg_addr 寄存器地址",
                        " * @retval uint8_t 读取到的寄存器值",
                        " */",
                        "uint8_t I2CDriver::read_register(uint8_t slave_addr, uint8_t reg_addr) {",
                        "    // 读取从设备寄存器值",
                        "    start();",
                        "    write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                        "    write_byte(reg_addr); // 发送寄存器地址",
                        "    start(); // 重复起始信号",
                        "    write_byte((slave_addr << 1) | 1); // 发送从设备地址，读模式",
                        "    send_nack(); // 发送非应答",
                        "    uint8_t data = read_byte();",
                        "    stop();",
                        "    return data;",
                        "}",
                        "",
                        "/**",
                        " * @brief 写入从设备寄存器值",
                        " * @param slave_addr 从设备地址",
                        " * @param reg_addr 寄存器地址",
                        " * @param data 要写入的数据",
                        " * @retval None",
                        " */",
                        "void I2CDriver::write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                        "    // 写入从设备寄存器值",
                        "    start();",
                        "    write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                        "    write_byte(reg_addr); // 发送寄存器地址",
                        "    write_byte(data); // 发送数据",
                        "    stop();",
                        "}"
                    ])
            elif peripheral == "SPI":
                if lib_type == "标准库":
                    source_code.extend([
                        "",
                        "/**",
                        " * @brief 发送一个字节数据",
                        " * @param byte 要发送的字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPIDriver::send_byte(uint8_t byte) {",
                        "    // 发送一个字节数据",
                        "    while (SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_TXE) == RESET);",
                        "    SPI_I2S_SendData(SPI1, byte);",
                        "    while (SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_RXNE) == RESET);",
                        "    return SPI_I2S_ReceiveData(SPI1);",
                        "}",
                        "",
                        "/**",
                        " * @brief 接收一个字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPIDriver::receive_byte(void) {",
                        "    // 接收一个字节数据",
                        "    return send_byte(0xFF);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送和接收数据",
                        " * @param tx_data 发送数据缓冲区",
                        " * @param rx_data 接收数据缓冲区",
                        " * @param length 数据长度",
                        " * @retval None",
                        " */",
                        "void SPIDriver::send_receive_data(uint8_t* tx_data, uint8_t* rx_data, uint16_t length) {",
                        "    // 发送和接收数据",
                        "    for (uint16_t i = 0; i < length; i++) {",
                        "        rx_data[i] = send_byte(tx_data[i]);",
                        "    }",
                        "}",
                        "",
                        "/**",
                        " * @brief 设置片选信号",
                        " * @param state 片选状态（0为选中，1为取消选中）",
                        " * @retval None",
                        " */",
                        "void SPIDriver::set_cs(uint8_t state) {",
                        "    // 设置片选信号",
                        "    if (state) {",
                        "        // 取消选中",
                        "    } else {",
                        "        // 选中",
                        "    }",
                        "}"
                    ])
                elif lib_type == "HAL库":
                    source_code.extend([
                        "",
                        "/**",
                        " * @brief 发送一个字节数据",
                        " * @param byte 要发送的字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPIDriver::send_byte(uint8_t byte) {",
                        "    // 发送一个字节数据",
                        "    uint8_t rx_data = 0;",
                        "    HAL_SPI_TransmitReceive(&hspi, &byte, &rx_data, 1, HAL_MAX_DELAY);",
                        "    return rx_data;",
                        "}",
                        "",
                        "/**",
                        " * @brief 接收一个字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPIDriver::receive_byte(void) {",
                        "    // 接收一个字节数据",
                        "    return send_byte(0xFF);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送和接收数据",
                        " * @param tx_data 发送数据缓冲区",
                        " * @param rx_data 接收数据缓冲区",
                        " * @param length 数据长度",
                        " * @retval None",
                        " */",
                        "void SPIDriver::send_receive_data(uint8_t* tx_data, uint8_t* rx_data, uint16_t length) {",
                        "    // 发送和接收数据",
                        "    HAL_SPI_TransmitReceive(&hspi, tx_data, rx_data, length, HAL_MAX_DELAY);",
                        "}",
                        "",
                        "/**",
                        " * @brief 设置片选信号",
                        " * @param state 片选状态（0为选中，1为取消选中）",
                        " * @retval None",
                        " */",
                        "void SPIDriver::set_cs(uint8_t state) {",
                        "    // 设置片选信号",
                        "    if (state) {",
                        "        // 取消选中",
                        "    } else {",
                        "        // 选中",
                        "    }",
                        "}"
                    ])
                else:  # LL库
                    source_code.extend([
                        "",
                        "/**",
                        " * @brief 发送一个字节数据",
                        " * @param byte 要发送的字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPIDriver::send_byte(uint8_t byte) {",
                        "    // 发送一个字节数据",
                        "    while (!LL_SPI_IsActiveFlag_TXE(SPI1));",
                        "    LL_SPI_TransmitData8(SPI1, byte);",
                        "    while (!LL_SPI_IsActiveFlag_RXNE(SPI1));",
                        "    return LL_SPI_ReceiveData8(SPI1);",
                        "}",
                        "",
                        "/**",
                        " * @brief 接收一个字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPIDriver::receive_byte(void) {",
                        "    // 接收一个字节数据",
                        "    return send_byte(0xFF);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送和接收数据",
                        " * @param tx_data 发送数据缓冲区",
                        " * @param rx_data 接收数据缓冲区",
                        " * @param length 数据长度",
                        " * @retval None",
                        " */",
                        "void SPIDriver::send_receive_data(uint8_t* tx_data, uint8_t* rx_data, uint16_t length) {",
                        "    // 发送和接收数据",
                        "    for (uint16_t i = 0; i < length; i++) {",
                        "        rx_data[i] = send_byte(tx_data[i]);",
                        "    }",
                        "}",
                        "",
                        "/**",
                        " * @brief 设置片选信号",
                        " * @param state 片选状态（0为选中，1为取消选中）",
                        " * @retval None",
                        " */",
                        "void SPIDriver::set_cs(uint8_t state) {",
                        "    // 设置片选信号",
                        "    if (state) {",
                        "        // 取消选中",
                        "    } else {",
                        "        // 选中",
                        "    }",
                        "}"
                    ])
            # 其他外设的C++操作函数实现...
        else:
            if peripheral == "GPIO":
                pin = params["pin"]
                # 解析引脚
                port = pin[1] if pin[0] == "P" else pin[0]
                pin_num = int(pin[2:] if pin[0] == "P" else pin[1:])
                port_map = {"A": "GPIOA", "B": "GPIOB", "C": "GPIOC", "D": "GPIOD"}
                
                source_code.extend([
                    "/**",
                    " * @brief 设置引脚为高电平",
                    " * @retval None",
                    " */",
                    f"void GPIO_set_high(void) {{",
                    "    // 设置引脚高电平",
                    f"    {port_map[port]}->BSRR = GPIO_Pin_{pin_num};",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚为低电平",
                    " * @retval None",
                    " */",
                    f"void GPIO_set_low(void) {{",
                    "    // 设置引脚低电平",
                    f"    {port_map[port]}->BRR = GPIO_Pin_{pin_num};",
                    "}",
                    "",
                    "/**",
                    " * @brief 翻转引脚电平",
                    " * @retval None",
                    " */",
                    f"void GPIO_toggle(void) {{",
                    "    // 翻转引脚电平",
                    f"    {port_map[port]}->ODR ^= GPIO_Pin_{pin_num};",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取引脚电平",
                    " * @retval uint8_t 引脚电平值（0或1）",
                    " */",
                    f"uint8_t GPIO_read(void) {{",
                    "    // 读取引脚电平",
                    f"    return GPIO_ReadInputDataBit({port_map[port]}, GPIO_Pin_{pin_num});",
                    "}"
                ])
            elif peripheral == "UART":
                source_code.extend([
                    "/**",
                    " * @brief 发送一个字节数据",
                    " * @param byte 要发送的字节数据",
                    " * @retval None",
                    " */",
                    "void UART_send_byte(uint8_t byte) {",
                    "    // 发送一个字节",
                    "    while (!LL_USART_IsActiveFlag_TXE(USART1));",
                    "    LL_USART_TransmitData8(USART1, byte);",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送字符串",
                    " * @param str 要发送的字符串指针",
                    " * @retval None",
                    " */",
                    "void UART_send_string(const char* str) {",
                    "    // 发送字符串",
                    "    while (*str) {",
                    "        UART_send_byte(*str++);",
                    "    }",
                    "}",
                    "",
                    "/**",
                    " * @brief 接收一个字节数据",
                    " * @retval uint8_t 接收到的字节数据",
                    " */",
                    "uint8_t UART_receive_byte(void) {",
                    "    // 接收一个字节",
                    "    while (!LL_USART_IsActiveFlag_RXNE(USART1));",
                    "    return LL_USART_ReceiveData8(USART1);",
                    "}",
                    "",
                    "/**",
                    " * @brief 接收字符串",
                    " * @param buffer 接收缓冲区指针",
                    " * @param length 缓冲区长度",
                    " * @retval None",
                    " */",
                    "void UART_receive_string(char* buffer, uint16_t length) {",
                    "    // 接收字符串",
                    "    uint16_t i = 0;",
                    "    while (i < length - 1) {",
                    "        buffer[i] = UART_receive_byte();",
                    "        if (buffer[i] == '\\0') break;",
                    "        i++;",
                    "    }",
                    "    buffer[i] = '\\0';",
                    "}",
                    "",
                    "/**",
                    " * @brief 配置UART中断",
                    " * @retval None",
                    " */",
                    "void UART_config_interrupt(void) {",
                    "    // 配置UART中断",
                    "    LL_USART_EnableIT_RXNE(USART1);",
                    "    NVIC_EnableIRQ(USART1_IRQn);",
                    "}"
                ])
            elif peripheral == "I2C":
                i2c_mode = params.get("i2c_mode", "硬件IIC")
                scl_pin = params["scl_pin"]
                sda_pin = params["sda_pin"]
                
                # 解析引脚
                scl_port = scl_pin[1] if scl_pin[0] == 'P' else scl_pin[0]
                scl_num = int(scl_pin[2:] if scl_pin[0] == 'P' else scl_pin[1:])
                sda_port = sda_pin[1] if sda_pin[0] == 'P' else sda_pin[0]
                sda_num = int(sda_pin[2:] if sda_pin[0] == 'P' else sda_pin[1:])
                
                port_map = {"A": "GPIOA", "B": "GPIOB", "C": "GPIOC", "D": "GPIOD"}
                
                if i2c_mode == "硬件IIC":
                    source_code.extend([
                        "",
                        "/**",
                        " * @brief 发送I2C起始信号",
                        " * @retval None",
                        " */",
                        "void I2C_start(void) {",
                        "    // 发送I2C起始信号",
                        "    I2C_GenerateSTART(I2C1, ENABLE);",
                        "    while (!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_MODE_SELECT));",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C停止信号",
                        " * @retval None",
                        " */",
                        "void I2C_stop(void) {",
                        "    // 发送I2C停止信号",
                        "    I2C_GenerateSTOP(I2C1, ENABLE);",
                        "    while (I2C_GetFlagStatus(I2C1, I2C_FLAG_STOPF));",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C应答信号",
                        " * @retval None",
                        " */",
                        "void I2C_send_ack(void) {",
                        "    // 发送I2C应答信号",
                        "    I2C_AcknowledgeConfig(I2C1, ENABLE);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C非应答信号",
                        " * @retval None",
                        " */",
                        "void I2C_send_nack(void) {",
                        "    // 发送I2C非应答信号",
                        "    I2C_AcknowledgeConfig(I2C1, DISABLE);",
                        "}",
                        "",
                        "/**",
                        " * @brief 读取一个字节数据",
                        " * @retval uint8_t 读取到的字节数据",
                        " */",
                        "uint8_t I2C_read_byte(void) {",
                        "    // 读取一个字节数据",
                        "    while (!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_RECEIVED));",
                        "    return I2C_ReceiveData(I2C1);",
                        "}",
                        "",
                        "/**",
                        " * @brief 写入一个字节数据",
                        " * @param byte 要写入的字节数据",
                        " * @retval None",
                        " */",
                        "void I2C_write_byte(uint8_t byte) {",
                        "    // 写入一个字节数据",
                        "    I2C_SendData(I2C1, byte);",
                        "    while (!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_TRANSMITTED));",
                        "}",
                        "",
                        "/**",
                        " * @brief 读取从设备寄存器值",
                        " * @param slave_addr 从设备地址",
                        " * @param reg_addr 寄存器地址",
                        " * @retval uint8_t 读取到的寄存器值",
                        " */",
                        "uint8_t I2C_read_register(uint8_t slave_addr, uint8_t reg_addr) {",
                        "    // 读取从设备寄存器值",
                        "    I2C_start();",
                        "    I2C_write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                        "    I2C_write_byte(reg_addr); // 发送寄存器地址",
                        "    I2C_start(); // 重复起始信号",
                        "    I2C_write_byte((slave_addr << 1) | 1); // 发送从设备地址，读模式",
                        "    I2C_send_nack(); // 发送非应答",
                        "    uint8_t data = I2C_read_byte();",
                        "    I2C_stop();",
                        "    return data;",
                        "}",
                        "",
                        "/**",
                        " * @brief 写入从设备寄存器值",
                        " * @param slave_addr 从设备地址",
                        " * @param reg_addr 寄存器地址",
                        " * @param data 要写入的数据",
                        " * @retval None",
                        " */",
                        "void I2C_write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                        "    // 写入从设备寄存器值",
                        "    I2C_start();",
                        "    I2C_write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                        "    I2C_write_byte(reg_addr); // 发送寄存器地址",
                        "    I2C_write_byte(data); // 发送数据",
                        "    I2C_stop();",
                        "}"
                    ])
                else:  # 软件模拟IIC
                    source_code.extend([
                        "",
                        "// 延时函数",
                        "void I2C_delay(uint32_t us) {",
                        "    uint32_t i = us * 8; // 简单延时",
                        "    while (i--);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C起始信号",
                        " * @retval None",
                        " */",
                        "void I2C_start(void) {",
                        "    // 发送I2C起始信号",
                        "    LL_GPIO_SetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 1",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 0",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C停止信号",
                        " * @retval None",
                        " */",
                        "void I2C_stop(void) {",
                        "    // 发送I2C停止信号",
                        "    LL_GPIO_ResetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 0",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_SetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 1",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C应答信号",
                        " * @retval None",
                        " */",
                        "void I2C_send_ack(void) {",
                        "    // 发送I2C应答信号",
                        "    LL_GPIO_ResetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 0",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送I2C非应答信号",
                        " * @retval None",
                        " */",
                        "void I2C_send_nack(void) {",
                        "    // 发送I2C非应答信号",
                        "    LL_GPIO_SetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 1",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 读取一个字节数据",
                        " * @retval uint8_t 读取到的字节数据",
                        " */",
                        "uint8_t I2C_read_byte(void) {",
                        "    // 读取一个字节数据",
                        "    uint8_t data = 0;",
                        "    LL_GPIO_SetPinMode(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ", LL_GPIO_MODE_INPUT);  // SDA = 输入",
                        "    for (int i = 7; i >= 0; i--) {",
                        "        LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "        I2C_delay(5);",
                        "        if (LL_GPIO_IsInputPinSet(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ")) {",
                        "            data |= (1 << i);",
                        "        }",
                        "        LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "        I2C_delay(5);",
                        "    }",
                        "    LL_GPIO_SetPinMode(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ", LL_GPIO_MODE_OUTPUT);  // SDA = 输出",
                        "    return data;",
                        "}",
                        "",
                        "/**",
                        " * @brief 写入一个字节数据",
                        " * @param byte 要写入的字节数据",
                        " * @retval None",
                        " */",
                        "void I2C_write_byte(uint8_t byte) {",
                        "    // 写入一个字节数据",
                        "    for (int i = 7; i >= 0; i--) {",
                        "        if (byte & (1 << i)) {",
                        "            LL_GPIO_SetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 1",
                        "        } else {",
                        "            LL_GPIO_ResetOutputPin(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ");  // SDA = 0",
                        "        }",
                        "        I2C_delay(5);",
                        "        LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "        I2C_delay(5);",
                        "        LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "        I2C_delay(5);",
                        "    }",
                        "    // 等待应答",
                        "    LL_GPIO_SetPinMode(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ", LL_GPIO_MODE_INPUT);  // SDA = 输入",
                        "    LL_GPIO_SetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 1",
                        "    I2C_delay(5);",
                        "    LL_GPIO_ResetOutputPin(" + port_map[scl_port] + ", LL_GPIO_PIN_" + str(scl_num) + ");  // SCL = 0",
                        "    LL_GPIO_SetPinMode(" + port_map[sda_port] + ", LL_GPIO_PIN_" + str(sda_num) + ", LL_GPIO_MODE_OUTPUT);  // SDA = 输出",
                        "    I2C_delay(5);",
                        "}",
                        "",
                        "/**",
                        " * @brief 读取从设备寄存器值",
                        " * @param slave_addr 从设备地址",
                        " * @param reg_addr 寄存器地址",
                        " * @retval uint8_t 读取到的寄存器值",
                        " */",
                        "uint8_t I2C_read_register(uint8_t slave_addr, uint8_t reg_addr) {",
                        "    // 读取从设备寄存器值",
                        "    I2C_start();",
                        "    I2C_write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                        "    I2C_write_byte(reg_addr); // 发送寄存器地址",
                        "    I2C_start(); // 重复起始信号",
                        "    I2C_write_byte((slave_addr << 1) | 1); // 发送从设备地址，读模式",
                        "    I2C_send_nack(); // 发送非应答",
                        "    uint8_t data = I2C_read_byte();",
                        "    I2C_stop();",
                        "    return data;",
                        "}",
                        "",
                        "/**",
                        " * @brief 写入从设备寄存器值",
                        " * @param slave_addr 从设备地址",
                        " * @param reg_addr 寄存器地址",
                        " * @param data 要写入的数据",
                        " * @retval None",
                        " */",
                        "void I2C_write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                        "    // 写入从设备寄存器值",
                        "    I2C_start();",
                        "    I2C_write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                        "    I2C_write_byte(reg_addr); // 发送寄存器地址",
                        "    I2C_write_byte(data); // 发送数据",
                        "    I2C_stop();",
                        "}"
                    ])
            elif peripheral == "SPI":
                if lib_type == "标准库":
                    source_code.extend([
                        "",
                        "/**",
                        " * @brief 发送一个字节数据",
                        " * @param byte 要发送的字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPI_send_byte(uint8_t byte) {",
                        "    // 发送一个字节数据",
                        "    while (SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_TXE) == RESET);",
                        "    SPI_I2S_SendData(SPI1, byte);",
                        "    while (SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_RXNE) == RESET);",
                        "    return SPI_I2S_ReceiveData(SPI1);",
                        "}",
                        "",
                        "/**",
                        " * @brief 接收一个字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPI_receive_byte(void) {",
                        "    // 接收一个字节数据",
                        "    return SPI_send_byte(0xFF);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送和接收数据",
                        " * @param tx_data 发送数据缓冲区",
                        " * @param rx_data 接收数据缓冲区",
                        " * @param length 数据长度",
                        " * @retval None",
                        " */",
                        "void SPI_send_receive_data(uint8_t* tx_data, uint8_t* rx_data, uint16_t length) {",
                        "    // 发送和接收数据",
                        "    for (uint16_t i = 0; i < length; i++) {",
                        "        rx_data[i] = SPI_send_byte(tx_data[i]);",
                        "    }",
                        "}",
                        "",
                        "/**",
                        " * @brief 设置片选信号",
                        " * @param state 片选状态（0为选中，1为取消选中）",
                        " * @retval None",
                        " */",
                        "void SPI_set_cs(uint8_t state) {",
                        "    // 设置片选信号",
                        "    if (state) {",
                        "        // 取消选中",
                        "    } else {",
                        "        // 选中",
                        "    }",
                        "}"
                    ])
                elif lib_type == "HAL库":
                    source_code.extend([
                        "",
                        "/**",
                        " * @brief 发送一个字节数据",
                        " * @param byte 要发送的字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPI_send_byte(uint8_t byte) {",
                        "    // 发送一个字节数据",
                        "    uint8_t rx_data = 0;",
                        "    HAL_SPI_TransmitReceive(&hspi, &byte, &rx_data, 1, HAL_MAX_DELAY);",
                        "    return rx_data;",
                        "}",
                        "",
                        "/**",
                        " * @brief 接收一个字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPI_receive_byte(void) {",
                        "    // 接收一个字节数据",
                        "    return SPI_send_byte(0xFF);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送和接收数据",
                        " * @param tx_data 发送数据缓冲区",
                        " * @param rx_data 接收数据缓冲区",
                        " * @param length 数据长度",
                        " * @retval None",
                        " */",
                        "void SPI_send_receive_data(uint8_t* tx_data, uint8_t* rx_data, uint16_t length) {",
                        "    // 发送和接收数据",
                        "    HAL_SPI_TransmitReceive(&hspi, tx_data, rx_data, length, HAL_MAX_DELAY);",
                        "}",
                        "",
                        "/**",
                        " * @brief 设置片选信号",
                        " * @param state 片选状态（0为选中，1为取消选中）",
                        " * @retval None",
                        " */",
                        "void SPI_set_cs(uint8_t state) {",
                        "    // 设置片选信号",
                        "    if (state) {",
                        "        // 取消选中",
                        "    } else {",
                        "        // 选中",
                        "    }",
                        "}"
                    ])
                else:  # LL库
                    source_code.extend([
                        "",
                        "/**",
                        " * @brief 发送一个字节数据",
                        " * @param byte 要发送的字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPI_send_byte(uint8_t byte) {",
                        "    // 发送一个字节数据",
                        "    while (!LL_SPI_IsActiveFlag_TXE(SPI1));",
                        "    LL_SPI_TransmitData8(SPI1, byte);",
                        "    while (!LL_SPI_IsActiveFlag_RXNE(SPI1));",
                        "    return LL_SPI_ReceiveData8(SPI1);",
                        "}",
                        "",
                        "/**",
                        " * @brief 接收一个字节数据",
                        " * @retval uint8_t 接收到的字节数据",
                        " */",
                        "uint8_t SPI_receive_byte(void) {",
                        "    // 接收一个字节数据",
                        "    return SPI_send_byte(0xFF);",
                        "}",
                        "",
                        "/**",
                        " * @brief 发送和接收数据",
                        " * @param tx_data 发送数据缓冲区",
                        " * @param rx_data 接收数据缓冲区",
                        " * @param length 数据长度",
                        " * @retval None",
                        " */",
                        "void SPI_send_receive_data(uint8_t* tx_data, uint8_t* rx_data, uint16_t length) {",
                        "    // 发送和接收数据",
                        "    for (uint16_t i = 0; i < length; i++) {",
                        "        rx_data[i] = SPI_send_byte(tx_data[i]);",
                        "    }",
                        "}",
                        "",
                        "/**",
                        " * @brief 设置片选信号",
                        " * @param state 片选状态（0为选中，1为取消选中）",
                        " * @retval None",
                        " */",
                        "void SPI_set_cs(uint8_t state) {",
                        "    // 设置片选信号",
                        "    if (state) {",
                        "        // 取消选中",
                        "    } else {",
                        "        // 选中",
                        "    }",
                        "}"
                    ])
            # 其他外设的C操作函数实现...
        
        # 添加中断处理函数（如果需要）
        if peripheral == "TIM":
            source_code.extend([
                "",
                "/**",
                " * @brief 定时器中断处理函数",
                " * @retval None",
                " */",
                "void TIM2_IRQHandler(void) {",
                "    if (TIM_GetITStatus(TIM2, TIM_IT_Update) != RESET) {",
                "        // 处理定时器中断",
                "        ",
                "        // 清除中断标志位",
                "        TIM_ClearITPendingBit(TIM2, TIM_IT_Update);",
                "    }",
                "}"
            ])
        
        return "\n".join(header_code), "\n".join(source_code)
    
    def generate_51_code(self, peripheral, language, lib_type, xtal, params):
        """生成51系列代码"""
        is_cpp = language == "C++语言"
        header_code = []
        source_code = []
        
        # 头文件内容
        if is_cpp:
            header_code.append('#include <c8051f020.h>')
        else:
            header_code.append('#include <reg51.h>')
        
        # 宏定义
        header_code.extend([
            "",
            "// 宏定义",
            f"#define FOSC {xtal * 1000000}L  // 系统晶振频率",
            f"#define T1MS (65536 - FOSC/12/1000)  // 1ms定时器初值",
            ""
        ])
        
        # 使用传入的外设参数
        # params = self.peripheral_params.get(peripheral, {})
        pin = params.get('pin', 'P1_0')
        baudrate = params.get('baudrate', 9600)
        channel = params.get('channel', 0)
        freq = params.get('frequency', 1000)
        duty = params.get('duty', 50)
        
        # 计算波特率初值
        if baudrate == 9600:
            baud_value = 0xFD
        elif baudrate == 4800:
            baud_value = 0xFA
        elif baudrate == 2400:
            baud_value = 0xF4
        elif baudrate == 1200:
            baud_value = 0xE8
        else:
            baud_value = 0xFD  # 默认9600
        
        # 函数声明
        if is_cpp:
            header_code.append("class " + peripheral + "Driver {")
            header_code.append("public:")
            header_code.append("    /**")
            header_code.append("     * @brief 初始化外设")
            header_code.append("     * @retval None")
            header_code.append("     */")
            header_code.append("    static void init();")
            if peripheral == "GPIO":
                header_code.append("    /**")
                header_code.append("     * @brief 设置引脚为高电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void setHigh();")
                header_code.append("    /**")
                header_code.append("     * @brief 设置引脚为低电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void setLow();")
                header_code.append("    /**")
                header_code.append("     * @brief 翻转引脚电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void toggle();")
                header_code.append("    /**")
                header_code.append("     * @brief 设置引脚电平")
                header_code.append("     * @param value 电平值（0或1）")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void set(uint8_t value);")
                header_code.append("    /**")
                header_code.append("     * @brief 读取引脚电平")
                header_code.append("     * @retval uint8_t 引脚电平值（0或1）")
                header_code.append("     */")
                header_code.append("    static uint8_t get();")
            elif peripheral == "UART":
                header_code.append("    /**")
                header_code.append("     * @brief 发送数据")
                header_code.append("     * @param data 要发送的数据")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void send(uint8_t data);")
                header_code.append("    /**")
                header_code.append("     * @brief 接收数据")
                header_code.append("     * @retval uint8_t 接收到的数据")
                header_code.append("     */")
                header_code.append("    static uint8_t receive();")
                header_code.append("    /**")
                header_code.append("     * @brief 发送字符串")
                header_code.append("     * @param str 要发送的字符串指针")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void sendString(const char *str);")
            header_code.append("};")
            source_code.append("#include \"" + peripheral.lower() + "_driver.h\"")
            source_code.append("")
            source_code.append("void " + peripheral + "Driver::init() {")
        else:
            header_code.append("/**")
            header_code.append(" * @brief 初始化外设")
            header_code.append(" * @retval None")
            header_code.append(" */")
            header_code.append("void " + peripheral + "_init(void);")
            if peripheral == "GPIO":
                header_code.append("/**")
                header_code.append(" * @brief 设置引脚为高电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_setHigh(void);")
                header_code.append("/**")
                header_code.append(" * @brief 设置引脚为低电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_setLow(void);")
                header_code.append("/**")
                header_code.append(" * @brief 翻转引脚电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_toggle(void);")
                header_code.append("/**")
                header_code.append(" * @brief 设置引脚电平")
                header_code.append(" * @param value 电平值（0或1）")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_set(uint8_t value);")
                header_code.append("/**")
                header_code.append(" * @brief 读取引脚电平")
                header_code.append(" * @retval uint8_t 引脚电平值（0或1）")
                header_code.append(" */")
                header_code.append("uint8_t " + peripheral + "_get(void);")
            elif peripheral == "UART":
                header_code.append("/**")
                header_code.append(" * @brief 发送数据")
                header_code.append(" * @param data 要发送的数据")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_send(uint8_t data);")
                header_code.append("/**")
                header_code.append(" * @brief 接收数据")
                header_code.append(" * @retval uint8_t 接收到的数据")
                header_code.append(" */")
                header_code.append("uint8_t " + peripheral + "_receive(void);")
                header_code.append("/**")
                header_code.append(" * @brief 发送字符串")
                header_code.append(" * @param str 要发送的字符串指针")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_sendString(const char *str);")
            source_code.append("#include \"" + peripheral.lower() + "_driver.h\"")
            source_code.append("")
            source_code.append("/**")
            source_code.append(" * @brief 初始化" + peripheral + "外设")
            source_code.append(" * @retval None")
            source_code.append(" */")
            source_code.append("void " + peripheral + "_init(void) {")
        
        # 根据外设生成初始化代码
        if peripheral == "GPIO":
            source_code.extend([
                "    // GPIO初始化",
                f"    {pin.rsplit('_', 1)[0]} = 0x00; // 初始化端口为低电平",
                f"    {pin.rsplit('_', 1)[0]}DIR = 0xFF; // 设置端口为输出"
            ])
        elif peripheral == "UART":
            source_code.extend([
                "    // UART初始化",
                "    TMOD = 0x20; // 定时器1工作在模式2",
                f"    TH1 = 0x{baud_value:02X}; // 波特率{baudrate} @ {xtal}MHz",
                f"    TL1 = 0x{baud_value:02X};",
                "    PCON = 0x00; // 波特率不加倍",
                "    SCON = 0x50; // 串口工作在模式1，允许接收",
                "    TR1 = 1; // 启动定时器1",
                "    ES = 1; // 允许串口中断",
                "    EA = 1; // 允许总中断"
            ])
        elif peripheral == "I2C":
            source_code.extend([
                "    // I2C初始化",
                "    // 51单片机没有硬件I2C，使用软件模拟",
                "    SDA = 1; // 数据线拉高",
                "    SCL = 1; // 时钟线拉高"
            ])
        elif peripheral == "SPI":
            source_code.extend([
                "    // SPI初始化",
                "    // 51单片机没有硬件SPI，使用软件模拟",
                "    // 配置相关引脚为输出",
                "    SS = 1; // 片选拉高",
                "    SCK = 0; // 时钟拉低",
                "    MOSI = 0; // 主出从入拉低"
            ])
        elif peripheral == "CAN":
            source_code.extend([
                "    // CAN初始化",
                "    // 51单片机没有硬件CAN，需要外接CAN控制器"
            ])
        elif peripheral == "ADC":
            source_code.extend([
                "    // ADC初始化",
                "    // 51单片机没有硬件ADC，需要外接ADC芯片"
            ])
        elif peripheral == "PWM":
            source_code.extend([
                "    // PWM初始化",
                "    // 使用定时器0生成PWM",
                "    TMOD = 0x01; // 定时器0工作在模式1",
                "    TH0 = 0xFF; // 初始值",
                "    TL0 = 0x00;",
                "    ET0 = 1; // 允许定时器0中断",
                "    EA = 1; // 允许总中断",
                "    TR0 = 1; // 启动定时器0"
            ])
        elif peripheral == "TIM":
            source_code.extend([
                "    // 定时器初始化",
                "    TMOD = 0x01; // 定时器0工作在模式1",
                "    TH0 = T1MS >> 8; // 1ms @ {xtal}MHz",
                "    TL0 = T1MS & 0xFF;",
                "    ET0 = 1; // 允许定时器0中断",
                "    EA = 1; // 允许总中断",
                "    TR0 = 1; // 启动定时器0"
            ])
        
        source_code.append("}")
        
        # 添加操作函数
        if is_cpp:
            if peripheral == "GPIO":
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 设置引脚为高电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::setHigh() {",
                    f"    {pin} = 1; // 设置引脚高电平",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚为低电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::setLow() {",
                    f"    {pin} = 0; // 设置引脚低电平",
                    "}",
                    "",
                    "/**",
                    " * @brief 翻转引脚电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::toggle() {",
                    f"    {pin} = ~{pin}; // 翻转引脚电平",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚电平",
                    " * @param value 电平值（0或1）",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::set(uint8_t value) {",
                    f"    {pin} = value; // 设置引脚电平",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取引脚电平",
                    " * @retval uint8_t 引脚电平值（0或1）",
                    " */",
                    "uint8_t " + peripheral + "Driver::get() {",
                    f"    return {pin}; // 读取引脚电平",
                    "}"
                ])
            elif peripheral == "UART":
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 发送数据",
                    " * @param data 要发送的数据",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::send(uint8_t data) {",
                    "    SBUF = data; // 发送数据",
                    "    while (!TI); // 等待发送完成",
                    "    TI = 0; // 清除发送标志",
                    "}",
                    "",
                    "/**",
                    " * @brief 接收数据",
                    " * @retval uint8_t 接收到的数据",
                    " */",
                    "uint8_t " + peripheral + "Driver::receive() {",
                    "    while (!RI); // 等待接收完成",
                    "    RI = 0; // 清除接收标志",
                    "    return SBUF; // 返回接收到的数据",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送字符串",
                    " * @param str 要发送的字符串指针",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::sendString(const char *str) {",
                    "    while (*str) {",
                    "        send(*str++);",
                    "    }",
                    "}"
                ])
            elif peripheral == "I2C":
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 发送I2C起始信号",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::start() {",
                    "    // 发送I2C起始信号",
                    "    SDA = 1;",
                    "    SCL = 1;",
                    "    SDA = 0;",
                    "    SCL = 0;",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C停止信号",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::stop() {",
                    "    // 发送I2C停止信号",
                    "    SDA = 0;",
                    "    SCL = 1;",
                    "    SDA = 1;",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C应答信号",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::send_ack() {",
                    "    // 发送I2C应答信号",
                    "    SDA = 0;",
                    "    SCL = 1;",
                    "    SCL = 0;",
                    "    SDA = 1;",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C非应答信号",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::send_nack() {",
                    "    // 发送I2C非应答信号",
                    "    SDA = 1;",
                    "    SCL = 1;",
                    "    SCL = 0;",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取一个字节数据",
                    " * @retval uint8_t 读取到的字节数据",
                    " */",
                    "uint8_t " + peripheral + "Driver::read_byte() {",
                    "    // 读取一个字节数据",
                    "    uint8_t data = 0;",
                    "    SDA = 1; // 释放SDA线",
                    "    for (uint8_t i = 0; i < 8; i++) {",
                    "        data <<= 1;",
                    "        SCL = 1;",
                    "        if (SDA) data |= 0x01;",
                    "        SCL = 0;",
                    "    }",
                    "    return data;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入一个字节数据",
                    " * @param byte 要写入的字节数据",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::write_byte(uint8_t byte) {",
                    "    // 写入一个字节数据",
                    "    for (uint8_t i = 0; i < 8; i++) {",
                    "        SDA = (byte & 0x80) ? 1 : 0;",
                    "        SCL = 1;",
                    "        SCL = 0;",
                    "        byte <<= 1;",
                    "    }",
                    "    // 等待应答",
                    "    SDA = 1; // 释放SDA线",
                    "    SCL = 1;",
                    "    SCL = 0;",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @retval uint8_t 读取到的寄存器值",
                    " */",
                    "uint8_t " + peripheral + "Driver::read_register(uint8_t slave_addr, uint8_t reg_addr) {",
                    "    // 读取从设备寄存器值",
                    "    start();",
                    "    write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                    "    write_byte(reg_addr); // 发送寄存器地址",
                    "    start(); // 重复起始信号",
                    "    write_byte((slave_addr << 1) | 1); // 发送从设备地址，读模式",
                    "    send_nack(); // 发送非应答",
                    "    uint8_t data = read_byte();",
                    "    stop();",
                    "    return data;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 要写入的数据",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                    "    // 写入从设备寄存器值",
                    "    start();",
                    "    write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                    "    write_byte(reg_addr); // 发送寄存器地址",
                    "    write_byte(data); // 发送数据",
                    "    stop();",
                    "}"
                ])
        else:
            if peripheral == "GPIO":
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 设置引脚为高电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_setHigh(void) {",
                    f"    {pin} = 1; // 设置引脚高电平",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚为低电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_setLow(void) {",
                    f"    {pin} = 0; // 设置引脚低电平",
                    "}",
                    "",
                    "/**",
                    " * @brief 翻转引脚电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_toggle(void) {",
                    f"    {pin} = ~{pin}; // 翻转引脚电平",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚电平",
                    " * @param value 电平值（0或1）",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_set(uint8_t value) {",
                    f"    {pin} = value; // 设置引脚电平",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取引脚电平",
                    " * @retval uint8_t 引脚电平值（0或1）",
                    " */",
                    "uint8_t " + peripheral + "_get(void) {",
                    f"    return {pin}; // 读取引脚电平",
                    "}"
                ])
            elif peripheral == "UART":
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 发送数据",
                    " * @param data 要发送的数据",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_send(uint8_t data) {",
                    "    SBUF = data; // 发送数据",
                    "    while (!TI); // 等待发送完成",
                    "    TI = 0; // 清除发送标志",
                    "}",
                    "",
                    "/**",
                    " * @brief 接收数据",
                    " * @retval uint8_t 接收到的数据",
                    " */",
                    "uint8_t " + peripheral + "_receive(void) {",
                    "    while (!RI); // 等待接收完成",
                    "    RI = 0; // 清除接收标志",
                    "    return SBUF; // 返回接收到的数据",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送字符串",
                    " * @param str 要发送的字符串指针",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_sendString(const char *str) {",
                    "    while (*str) {",
                    "        " + peripheral + "_send(*str++);",
                    "    }",
                    "}"
                ])
            elif peripheral == "I2C":
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 发送I2C起始信号",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_start(void) {",
                    "    // 发送I2C起始信号",
                    "    SDA = 1;",
                    "    SCL = 1;",
                    "    SDA = 0;",
                    "    SCL = 0;",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C停止信号",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_stop(void) {",
                    "    // 发送I2C停止信号",
                    "    SDA = 0;",
                    "    SCL = 1;",
                    "    SDA = 1;",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C应答信号",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_send_ack(void) {",
                    "    // 发送I2C应答信号",
                    "    SDA = 0;",
                    "    SCL = 1;",
                    "    SCL = 0;",
                    "    SDA = 1;",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C非应答信号",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_send_nack(void) {",
                    "    // 发送I2C非应答信号",
                    "    SDA = 1;",
                    "    SCL = 1;",
                    "    SCL = 0;",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取一个字节数据",
                    " * @retval uint8_t 读取到的字节数据",
                    " */",
                    "uint8_t " + peripheral + "_read_byte(void) {",
                    "    // 读取一个字节数据",
                    "    uint8_t data = 0;",
                    "    SDA = 1; // 释放SDA线",
                    "    for (uint8_t i = 0; i < 8; i++) {",
                    "        data <<= 1;",
                    "        SCL = 1;",
                    "        if (SDA) data |= 0x01;",
                    "        SCL = 0;",
                    "    }",
                    "    return data;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入一个字节数据",
                    " * @param byte 要写入的字节数据",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_write_byte(uint8_t byte) {",
                    "    // 写入一个字节数据",
                    "    for (uint8_t i = 0; i < 8; i++) {",
                    "        SDA = (byte & 0x80) ? 1 : 0;",
                    "        SCL = 1;",
                    "        SCL = 0;",
                    "        byte <<= 1;",
                    "    }",
                    "    // 等待应答",
                    "    SDA = 1; // 释放SDA线",
                    "    SCL = 1;",
                    "    SCL = 0;",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @retval uint8_t 读取到的寄存器值",
                    " */",
                    "uint8_t " + peripheral + "_read_register(uint8_t slave_addr, uint8_t reg_addr) {",
                    "    // 读取从设备寄存器值",
                    "    " + peripheral + "_start();",
                    "    " + peripheral + "_write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                    "    " + peripheral + "_write_byte(reg_addr); // 发送寄存器地址",
                    "    " + peripheral + "_start(); // 重复起始信号",
                    "    " + peripheral + "_write_byte((slave_addr << 1) | 1); // 发送从设备地址，读模式",
                    "    " + peripheral + "_send_nack(); // 发送非应答",
                    "    uint8_t data = " + peripheral + "_read_byte();",
                    "    " + peripheral + "_stop();",
                    "    return data;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 要写入的数据",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                    "    // 写入从设备寄存器值",
                    "    " + peripheral + "_start();",
                    "    " + peripheral + "_write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                    "    " + peripheral + "_write_byte(reg_addr); // 发送寄存器地址",
                    "    " + peripheral + "_write_byte(data); // 发送数据",
                    "    " + peripheral + "_stop();",
                    "}"
                ])
        
        # 添加中断处理函数（如果需要）
        if peripheral in ["PWM", "TIM"]:
            source_code.extend([
                "",
                "/**",
                " * @brief 定时器0中断处理函数",
                " * @retval None",
                " */",
                "void Timer0_ISR() interrupt 1 {",
                "    static unsigned char count = 0;",
                "    ",
                "    // 重新加载定时器值",
                "    TH0 = T1MS >> 8;",
                "    TL0 = T1MS & 0xFF;",
                "    ",
                "    count++;",
                "    if (count >= 1000) { // 1秒",
                "        count = 0;",
                "        // 在这里添加需要执行的代码",
                "    }",
                "}"
            ])
        
        return "\n".join(header_code), "\n".join(source_code)
    
    def generate_esp32_code(self, peripheral, language, lib_type, xtal, params):
        """生成ESP32代码"""
        is_cpp = language == "C++语言"
        header_code = []
        source_code = []
        
        # 头文件内容
        if is_cpp:
            header_code.append('#include <cstdint>')
        else:
            header_code.append('#include <stdint.h>')
        header_code.append('#include "freertos/FreeRTOS.h"')
        header_code.append('#include "freertos/task.h"')
        header_code.append('#include "driver/gpio.h"')
        
        # 根据外设添加相应的头文件
        if peripheral == "UART":
            header_code.append('#include "driver/uart.h"')
        elif peripheral == "I2C":
            header_code.append('#include "driver/i2c.h"')
        elif peripheral == "SPI":
            header_code.append('#include "driver/spi_master.h"')
        elif peripheral == "CAN":
            header_code.append('#include "driver/can.h"')
        elif peripheral == "ADC":
            header_code.append('#include "driver/adc.h"')
        elif peripheral == "PWM":
            header_code.append('#include "driver/ledc.h"')
        elif peripheral == "TIM":
            header_code.append('#include "driver/timer.h"')
        
        # 宏定义
        header_code.extend([
            "",
            "// 宏定义",
            f"#define XTAL_FREQ {xtal * 1000000}  // 系统晶振频率",
            ""
        ])
        
        # 使用传入的外设参数
        # params = self.peripheral_params.get(peripheral, {})
        pin = params.get('pin', 'GPIO_NUM_2')
        baudrate = params.get('baudrate', 115200)
        channel = params.get('channel', 0)
        freq = params.get('frequency', 1000)
        duty = params.get('duty', 50)
        
        # 函数声明
        if is_cpp:
            header_code.append("class " + peripheral + "Driver {")
            header_code.append("public:")
            header_code.append("    /**")
            header_code.append("     * @brief 初始化外设")
            header_code.append("     * @retval esp_err_t 初始化结果")
            header_code.append("     */")
            header_code.append("    static esp_err_t init();")
            if peripheral == "GPIO":
                header_code.append("    /**")
                header_code.append("     * @brief 设置引脚为高电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void setHigh();")
                header_code.append("    /**")
                header_code.append("     * @brief 设置引脚为低电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void setLow();")
                header_code.append("    /**")
                header_code.append("     * @brief 翻转引脚电平")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void toggle();")
                header_code.append("    /**")
                header_code.append("     * @brief 设置引脚电平")
                header_code.append("     * @param value 电平值（0或1）")
                header_code.append("     * @retval None")
                header_code.append("     */")
                header_code.append("    static void set(uint8_t value);")
                header_code.append("    /**")
                header_code.append("     * @brief 读取引脚电平")
                header_code.append("     * @retval uint8_t 引脚电平值（0或1）")
                header_code.append("     */")
                header_code.append("    static uint8_t get();")
            elif peripheral == "UART":
                header_code.append("    /**")
                header_code.append("     * @brief 发送数据")
                header_code.append("     * @param data 要发送的数据")
                header_code.append("     * @retval esp_err_t 发送结果")
                header_code.append("     */")
                header_code.append("    static esp_err_t send(uint8_t data);")
                header_code.append("    /**")
                header_code.append("     * @brief 接收数据")
                header_code.append("     * @param data 接收数据的缓冲区指针")
                header_code.append("     * @retval esp_err_t 接收结果")
                header_code.append("     */")
                header_code.append("    static esp_err_t receive(uint8_t *data);")
                header_code.append("    /**")
                header_code.append("     * @brief 发送字符串")
                header_code.append("     * @param str 要发送的字符串指针")
                header_code.append("     * @retval esp_err_t 发送结果")
                header_code.append("     */")
                header_code.append("    static esp_err_t sendString(const char *str);")
            header_code.append("};")
            source_code.append("#include \"" + peripheral.lower() + "_driver.h\"")
            source_code.append("")
            source_code.append("esp_err_t " + peripheral + "Driver::init() {")
        else:
            header_code.append("/**")
            header_code.append(" * @brief 初始化外设")
            header_code.append(" * @retval esp_err_t 初始化结果")
            header_code.append(" */")
            header_code.append("esp_err_t " + peripheral + "_init(void);")
            if peripheral == "GPIO":
                header_code.append("/**")
                header_code.append(" * @brief 设置引脚为高电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_setHigh(void);")
                header_code.append("/**")
                header_code.append(" * @brief 设置引脚为低电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_setLow(void);")
                header_code.append("/**")
                header_code.append(" * @brief 翻转引脚电平")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_toggle(void);")
                header_code.append("/**")
                header_code.append(" * @brief 设置引脚电平")
                header_code.append(" * @param value 电平值（0或1）")
                header_code.append(" * @retval None")
                header_code.append(" */")
                header_code.append("void " + peripheral + "_set(uint8_t value);")
                header_code.append("/**")
                header_code.append(" * @brief 读取引脚电平")
                header_code.append(" * @retval uint8_t 引脚电平值（0或1）")
                header_code.append(" */")
                header_code.append("uint8_t " + peripheral + "_get(void);")
            elif peripheral == "UART":
                header_code.append("/**")
                header_code.append(" * @brief 发送数据")
                header_code.append(" * @param data 要发送的数据")
                header_code.append(" * @retval esp_err_t 发送结果")
                header_code.append(" */")
                header_code.append("esp_err_t " + peripheral + "_send(uint8_t data);")
                header_code.append("/**")
                header_code.append(" * @brief 接收数据")
                header_code.append(" * @param data 接收数据的缓冲区指针")
                header_code.append(" * @retval esp_err_t 接收结果")
                header_code.append(" */")
                header_code.append("esp_err_t " + peripheral + "_receive(uint8_t *data);")
                header_code.append("/**")
                header_code.append(" * @brief 发送字符串")
                header_code.append(" * @param str 要发送的字符串指针")
                header_code.append(" * @retval esp_err_t 发送结果")
                header_code.append(" */")
                header_code.append("esp_err_t " + peripheral + "_sendString(const char *str);")
            source_code.append("#include \"" + peripheral.lower() + "_driver.h\"")
            source_code.append("")
            source_code.append("esp_err_t " + peripheral + "_init(void) {")
        
        # 根据外设生成初始化代码
        if peripheral == "GPIO":
            source_code.extend([
                "    // GPIO初始化",
                "    gpio_config_t io_conf;",
                "    ",
                "    // 禁用中断",
                "    io_conf.intr_type = GPIO_INTR_DISABLE;",
                "    // 设置为输出模式",
                "    io_conf.mode = GPIO_MODE_OUTPUT;",
                "    // 位掩码设置要配置的引脚",
                f"    io_conf.pin_bit_mask = (1ULL << {pin});",
                "    // 禁用下拉模式",
                "    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;",
                "    // 禁用上拉模式",
                "    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;",
                "    // 配置GPIO",
                "    gpio_config(&io_conf);",
                "    ",
                "    return ESP_OK;"
            ])
        elif peripheral == "UART":
            source_code.extend([
                "    // UART初始化",
                "    uart_config_t uart_config = {",
                f"        .baud_rate = {baudrate},",
                "        .data_bits = UART_DATA_8_BITS,",
                "        .parity = UART_PARITY_DISABLE,",
                "        .stop_bits = UART_STOP_BITS_1,",
                "        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,",
                "        .source_clk = UART_SCLK_APB,",
                "    };",
                "    ",
                "    // 配置UART参数",
                "    uart_param_config(UART_NUM_0, &uart_config);",
                "    ",
                "    // 设置UART引脚",
                "    uart_set_pin(UART_NUM_0, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);",
                "    ",
                "    // 安装UART驱动",
                "    uart_driver_install(UART_NUM_0, 1024, 0, 0, NULL, 0);",
                "    ",
                "    return ESP_OK;"
            ])
        elif peripheral == "I2C":
            source_code.extend([
                "    // I2C初始化",
                "    i2c_config_t conf;",
                "    conf.mode = I2C_MODE_MASTER;",
                "    conf.sda_io_num = GPIO_NUM_21;",
                "    conf.sda_pullup_en = GPIO_PULLUP_ENABLE;",
                "    conf.scl_io_num = GPIO_NUM_22;",
                "    conf.scl_pullup_en = GPIO_PULLUP_ENABLE;",
                "    conf.master.clk_speed = 100000; // 100kHz",
                "    ",
                "    i2c_param_config(I2C_NUM_0, &conf);",
                "    i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0);",
                "    ",
                "    return ESP_OK;"
            ])
        elif peripheral == "SPI":
            source_code.extend([
                "    // SPI初始化",
                "    spi_bus_config_t bus_config = {",
                "        .miso_io_num = GPIO_NUM_19,",
                "        .mosi_io_num = GPIO_NUM_23,",
                "        .sclk_io_num = GPIO_NUM_18,",
                "        .quadwp_io_num = -1,",
                "        .quadhd_io_num = -1,",
                "        .max_transfer_sz = 4096,",
                "    };",
                "    ",
                "    spi_bus_initialize(SPI2_HOST, &bus_config, SPI_DMA_CH_AUTO);",
                "    ",
                "    return ESP_OK;"
            ])
        elif peripheral == "CAN":
            source_code.extend([
                "    // CAN初始化",
                "    can_general_config_t g_config = CAN_GENERAL_CONFIG_DEFAULT(GPIO_NUM_25, GPIO_NUM_26, CAN_MODE_NORMAL);",
                "    can_timing_config_t t_config = CAN_TIMING_CONFIG_500KBITS();",
                "    can_filter_config_t f_config = CAN_FILTER_CONFIG_ACCEPT_ALL();",
                "    ",
                "    can_driver_install(&g_config, &t_config, &f_config);",
                "    can_start();",
                "    ",
                "    return ESP_OK;"
            ])
        elif peripheral == "ADC":
            source_code.extend([
                "    // ADC初始化",
                "    adc1_config_width(ADC_WIDTH_BIT_12);",
                "    adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_11);",
                "    ",
                "    return ESP_OK;"
            ])
        elif peripheral == "PWM":
            source_code.extend([
                "    // PWM初始化",
                "    ledc_timer_config_t timer_conf = {",
                "        .duty_resolution = LEDC_TIMER_10_BIT,",
                f"        .freq_hz = {freq},",
                "        .speed_mode = LEDC_LOW_SPEED_MODE,",
                f"        .timer_num = LEDC_TIMER_{channel},",
                "    };",
                "    ledc_timer_config(&timer_conf);",
                "    ",
                "    ledc_channel_config_t channel_conf = {",
                f"        .gpio_num = {pin},",
                "        .speed_mode = LEDC_LOW_SPEED_MODE,",
                f"        .channel = LEDC_CHANNEL_{channel},",
                f"        .timer_sel = LEDC_TIMER_{channel},",
                f"        .duty = ({duty} * 1023) / 100, // 转换为10位占空比",
                "    };",
                "    ledc_channel_config(&channel_conf);",
                "    ",
                "    return ESP_OK;"
            ])
        elif peripheral == "TIM":
            source_code.extend([
                "    // 定时器初始化",
                "    timer_config_t config = {",
                "        .divider = 80,",
                "        .counter_dir = TIMER_COUNT_UP,",
                "        .counter_en = TIMER_PAUSE,",
                "        .alarm_en = TIMER_ALARM_EN,",
                "        .auto_reload = TIMER_AUTORELOAD_EN,",
                "    };",
                "    ",
                "    timer_init(TIMER_GROUP_0, TIMER_0, &config);",
                "    timer_set_counter_value(TIMER_GROUP_0, TIMER_0, 0);",
                "    timer_set_alarm_value(TIMER_GROUP_0, TIMER_0, 1000000); // 1秒",
                "    timer_enable_intr(TIMER_GROUP_0, TIMER_0);",
                "    timer_start(TIMER_GROUP_0, TIMER_0);",
                "    ",
                "    return ESP_OK;"
            ])
        
        source_code.append("}")
        
        # 添加GPIO操作函数
        if peripheral == "GPIO":
            if is_cpp:
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 设置引脚为高电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::setHigh() {",
                    f"    gpio_set_level({pin}, 1);",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚为低电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::setLow() {",
                    f"    gpio_set_level({pin}, 0);",
                    "}",
                    "",
                    "/**",
                    " * @brief 翻转引脚电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::toggle() {",
                    f"    gpio_set_level({pin}, !gpio_get_level({pin}));",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚电平",
                    " * @param value 电平值（0或1）",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "Driver::set(uint8_t value) {",
                    f"    gpio_set_level({pin}, value);",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取引脚电平",
                    " * @retval uint8_t 引脚电平值（0或1）",
                    " */",
                    "uint8_t " + peripheral + "Driver::get() {",
                    f"    return gpio_get_level({pin});",
                    "}"
                ])
            else:
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 设置引脚为高电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_setHigh(void) {",
                    f"    gpio_set_level({pin}, 1);",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚为低电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_setLow(void) {",
                    f"    gpio_set_level({pin}, 0);",
                    "}",
                    "",
                    "/**",
                    " * @brief 翻转引脚电平",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_toggle(void) {",
                    f"    gpio_set_level({pin}, !gpio_get_level({pin}));",
                    "}",
                    "",
                    "/**",
                    " * @brief 设置引脚电平",
                    " * @param value 电平值（0或1）",
                    " * @retval None",
                    " */",
                    "void " + peripheral + "_set(uint8_t value) {",
                    f"    gpio_set_level({pin}, value);",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取引脚电平",
                    " * @retval uint8_t 引脚电平值（0或1）",
                    " */",
                    "uint8_t " + peripheral + "_get(void) {",
                    f"    return gpio_get_level({pin});",
                    "}"
                ])
        
        # 添加UART操作函数
        elif peripheral == "UART":
            if is_cpp:
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 发送数据",
                    " * @param data 要发送的数据",
                    " * @retval esp_err_t 发送结果",
                    " */",
                    "esp_err_t " + peripheral + "Driver::send(uint8_t data) {",
                    "    return uart_write_bytes(UART_NUM_0, (const char *)&data, 1);",
                    "}",
                    "",
                    "/**",
                    " * @brief 接收数据",
                    " * @param data 接收数据的缓冲区指针",
                    " * @retval esp_err_t 接收结果",
                    " */",
                    "esp_err_t " + peripheral + "Driver::receive(uint8_t *data) {",
                    "    int len = uart_read_bytes(UART_NUM_0, data, 1, pdMS_TO_TICKS(100));",
                    "    return len == 1 ? ESP_OK : ESP_FAIL;",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送字符串",
                    " * @param str 要发送的字符串指针",
                    " * @retval esp_err_t 发送结果",
                    " */",
                    "esp_err_t " + peripheral + "Driver::sendString(const char *str) {",
                    "    return uart_write_bytes(UART_NUM_0, str, strlen(str));",
                    "}"
                ])
            else:
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 发送数据",
                    " * @param data 要发送的数据",
                    " * @retval esp_err_t 发送结果",
                    " */",
                    "esp_err_t " + peripheral + "_send(uint8_t data) {",
                    "    return uart_write_bytes(UART_NUM_0, (const char *)&data, 1);",
                    "}",
                    "",
                    "/**",
                    " * @brief 接收数据",
                    " * @param data 接收数据的缓冲区指针",
                    " * @retval esp_err_t 接收结果",
                    " */",
                    "esp_err_t " + peripheral + "_receive(uint8_t *data) {",
                    "    int len = uart_read_bytes(UART_NUM_0, data, 1, pdMS_TO_TICKS(100));",
                    "    return len == 1 ? ESP_OK : ESP_FAIL;",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送字符串",
                    " * @param str 要发送的字符串指针",
                    " * @retval esp_err_t 发送结果",
                    " */",
                    "esp_err_t " + peripheral + "_sendString(const char *str) {",
                    "    return uart_write_bytes(UART_NUM_0, str, strlen(str));",
                    "}"
                ])
        # 添加I2C操作函数
        elif peripheral == "I2C":
            if is_cpp:
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 读取从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 读取数据的缓冲区指针",
                    " * @retval esp_err_t 读取结果",
                    " */",
                    "esp_err_t " + peripheral + "Driver::read_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t *data) {",
                    "    i2c_cmd_handle_t cmd = i2c_cmd_link_create();",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_WRITE, true);",
                    "    i2c_master_write_byte(cmd, reg_addr, true);",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_READ, true);",
                    "    i2c_master_read_byte(cmd, data, I2C_MASTER_NACK);",
                    "    i2c_master_stop(cmd);",
                    "    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(1000));",
                    "    i2c_cmd_link_delete(cmd);",
                    "    return ret;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 要写入的数据",
                    " * @retval esp_err_t 写入结果",
                    " */",
                    "esp_err_t " + peripheral + "Driver::write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                    "    i2c_cmd_handle_t cmd = i2c_cmd_link_create();",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_WRITE, true);",
                    "    i2c_master_write_byte(cmd, reg_addr, true);",
                    "    i2c_master_write_byte(cmd, data, true);",
                    "    i2c_master_stop(cmd);",
                    "    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(1000));",
                    "    i2c_cmd_link_delete(cmd);",
                    "    return ret;",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取多个字节数据",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 读取数据的缓冲区指针",
                    " * @param len 要读取的字节数",
                    " * @retval esp_err_t 读取结果",
                    " */",
                    "esp_err_t " + peripheral + "Driver::read_bytes(uint8_t slave_addr, uint8_t reg_addr, uint8_t *data, size_t len) {",
                    "    i2c_cmd_handle_t cmd = i2c_cmd_link_create();",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_WRITE, true);",
                    "    i2c_master_write_byte(cmd, reg_addr, true);",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_READ, true);",
                    "    if (len > 1) {",
                    "        i2c_master_read(cmd, data, len - 1, I2C_MASTER_ACK);",
                    "    }",
                    "    i2c_master_read_byte(cmd, data + len - 1, I2C_MASTER_NACK);",
                    "    i2c_master_stop(cmd);",
                    "    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(1000));",
                    "    i2c_cmd_link_delete(cmd);",
                    "    return ret;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入多个字节数据",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 要写入的数据指针",
                    " * @param len 要写入的字节数",
                    " * @retval esp_err_t 写入结果",
                    " */",
                    "esp_err_t " + peripheral + "Driver::write_bytes(uint8_t slave_addr, uint8_t reg_addr, const uint8_t *data, size_t len) {",
                    "    i2c_cmd_handle_t cmd = i2c_cmd_link_create();",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_WRITE, true);",
                    "    i2c_master_write_byte(cmd, reg_addr, true);",
                    "    i2c_master_write(cmd, (uint8_t *)data, len, true);",
                    "    i2c_master_stop(cmd);",
                    "    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(1000));",
                    "    i2c_cmd_link_delete(cmd);",
                    "    return ret;",
                    "}"
                ])
            else:
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 读取从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 读取数据的缓冲区指针",
                    " * @retval esp_err_t 读取结果",
                    " */",
                    "esp_err_t " + peripheral + "_read_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t *data) {",
                    "    i2c_cmd_handle_t cmd = i2c_cmd_link_create();",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_WRITE, true);",
                    "    i2c_master_write_byte(cmd, reg_addr, true);",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_READ, true);",
                    "    i2c_master_read_byte(cmd, data, I2C_MASTER_NACK);",
                    "    i2c_master_stop(cmd);",
                    "    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(1000));",
                    "    i2c_cmd_link_delete(cmd);",
                    "    return ret;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 要写入的数据",
                    " * @retval esp_err_t 写入结果",
                    " */",
                    "esp_err_t " + peripheral + "_write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                    "    i2c_cmd_handle_t cmd = i2c_cmd_link_create();",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_WRITE, true);",
                    "    i2c_master_write_byte(cmd, reg_addr, true);",
                    "    i2c_master_write_byte(cmd, data, true);",
                    "    i2c_master_stop(cmd);",
                    "    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(1000));",
                    "    i2c_cmd_link_delete(cmd);",
                    "    return ret;",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取多个字节数据",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 读取数据的缓冲区指针",
                    " * @param len 要读取的字节数",
                    " * @retval esp_err_t 读取结果",
                    " */",
                    "esp_err_t " + peripheral + "_read_bytes(uint8_t slave_addr, uint8_t reg_addr, uint8_t *data, size_t len) {",
                    "    i2c_cmd_handle_t cmd = i2c_cmd_link_create();",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_WRITE, true);",
                    "    i2c_master_write_byte(cmd, reg_addr, true);",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_READ, true);",
                    "    if (len > 1) {",
                    "        i2c_master_read(cmd, data, len - 1, I2C_MASTER_ACK);",
                    "    }",
                    "    i2c_master_read_byte(cmd, data + len - 1, I2C_MASTER_NACK);",
                    "    i2c_master_stop(cmd);",
                    "    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(1000));",
                    "    i2c_cmd_link_delete(cmd);",
                    "    return ret;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入多个字节数据",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 要写入的数据指针",
                    " * @param len 要写入的字节数",
                    " * @retval esp_err_t 写入结果",
                    " */",
                    "esp_err_t " + peripheral + "_write_bytes(uint8_t slave_addr, uint8_t reg_addr, const uint8_t *data, size_t len) {",
                    "    i2c_cmd_handle_t cmd = i2c_cmd_link_create();",
                    "    i2c_master_start(cmd);",
                    "    i2c_master_write_byte(cmd, (slave_addr << 1) | I2C_MASTER_WRITE, true);",
                    "    i2c_master_write_byte(cmd, reg_addr, true);",
                    "    i2c_master_write(cmd, (uint8_t *)data, len, true);",
                    "    i2c_master_stop(cmd);",
                    "    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(1000));",
                    "    i2c_cmd_link_delete(cmd);",
                    "    return ret;",
                    "}"
                ])
        
        return "\n".join(header_code), "\n".join(source_code)
    
    def generate_gd32_code(self, peripheral, language, params):
        """生成GD32代码"""
        header_code = []
        source_code = []
        is_cpp = language == "C++语言"
        
        # 头文件
        if is_cpp:
            header_code.append('#include <cstdint>')
        else:
            header_code.append('#include <stdint.h>')
        header_code.append('#include "gd32f10x.h"')
        
        header_code.append("")
        
        # 函数声明
        if is_cpp:
            header_code.append("class " + peripheral + "Driver {")
            header_code.append("public:")
            header_code.append("    static void init();")
            if peripheral == "UART":
                header_code.extend([
                    "    static void send_byte(uint8_t byte);",
                    "    static void send_string(const char* str);",
                    "    static uint8_t receive_byte();",
                    "    static void receive_string(char* buffer, uint16_t length);",
                    "    static void config_interrupt();"
                ])
            header_code.append("};")
        else:
            header_code.append("void " + peripheral + "_init(void);")
            if peripheral == "UART":
                header_code.extend([
                    "void UART_send_byte(uint8_t byte);",
                    "void UART_send_string(const char* str);",
                    "uint8_t UART_receive_byte(void);",
                    "void UART_receive_string(char* buffer, uint16_t length);",
                    "void UART_config_interrupt(void);"
                ])
        
        # 源文件包含头文件
        source_code.extend([
            f"#include \"{peripheral.lower()}_driver.h\""
        ])
        
        # 函数实现
        if is_cpp:
            source_code.append("void " + peripheral + "Driver::init() {")
        else:
            source_code.append("void " + peripheral + "_init(void) {")
        
        # 根据外设生成初始化代码
        if peripheral == "GPIO":
            pin = params.get('pin', 'PA0')
            mode = params.get('mode', '输出')
            level = params.get('level', '低')
            pull = params.get('pull', '无')
            
            # 解析引脚
            port = pin[1] if pin[0] == 'P' else pin[0]
            pin_num = pin[2:] if pin[0] == 'P' else pin[1:]
            
            port_map = {"A": "GPIOA", "B": "GPIOB", "C": "GPIOC", "D": "GPIOD"}
            rcu_map = {"A": "RCU_GPIOA", "B": "RCU_GPIOB", "C": "RCU_GPIOC", "D": "RCU_GPIOD"}
            pin_map = {"0": "GPIO_PIN_0", "1": "GPIO_PIN_1", "2": "GPIO_PIN_2", "3": "GPIO_PIN_3", "4": "GPIO_PIN_4", "5": "GPIO_PIN_5", "6": "GPIO_PIN_6", "7": "GPIO_PIN_7", "8": "GPIO_PIN_8", "9": "GPIO_PIN_9", "10": "GPIO_PIN_10", "11": "GPIO_PIN_11", "12": "GPIO_PIN_12", "13": "GPIO_PIN_13", "14": "GPIO_PIN_14", "15": "GPIO_PIN_15"}
            
            mode_map = {"输入": "GPIO_MODE_IN_FLOATING", "输出": "GPIO_MODE_OUT_PP"}
            pull_map = {"无": "GPIO_MODE_IN_FLOATING", "上拉": "GPIO_MODE_IPU", "下拉": "GPIO_MODE_IPD"}
            
            source_code.extend([
                "    // GPIO初始化",
                f"    rcu_periph_clock_enable({rcu_map[port]});",
                "    ",
                f"    // 配置{pin}为{mode}",
            ])
            
            if mode == "输入":
                if pull != "无":
                    source_code.append(f"    gpio_init({port_map[port]}, {pull_map[pull]}, GPIO_OSPEED_50MHZ, {pin_map[pin_num]});")
                else:
                    source_code.append(f"    gpio_init({port_map[port]}, {mode_map[mode]}, GPIO_OSPEED_50MHZ, {pin_map[pin_num]});")
            else:
                source_code.append(f"    gpio_init({port_map[port]}, {mode_map[mode]}, GPIO_OSPEED_50MHZ, {pin_map[pin_num]});")
                source_code.append(f"    {'gpio_bit_set(' + port_map[port] + ', ' + pin_map[pin_num] + ');' if level == '高' else 'gpio_bit_reset(' + port_map[port] + ', ' + pin_map[pin_num] + ');'}")
        elif peripheral == "UART":
            baudrate = params.get('baudrate', 9600)
            tx_pin = params.get('tx_pin', 'PA9')
            rx_pin = params.get('rx_pin', 'PA10')
            
            # 解析引脚
            tx_port = tx_pin[1] if tx_pin[0] == 'P' else tx_pin[0]
            tx_num = tx_pin[2:] if tx_pin[0] == 'P' else tx_pin[1:]
            rx_port = rx_pin[1] if rx_pin[0] == 'P' else rx_pin[0]
            rx_num = rx_pin[2:] if rx_pin[0] == 'P' else rx_pin[1:]
            
            port_map = {"A": "GPIOA", "B": "GPIOB", "C": "GPIOC", "D": "GPIOD"}
            rcu_map = {"A": "RCU_GPIOA", "B": "RCU_GPIOB", "C": "RCU_GPIOC", "D": "RCU_GPIOD"}
            pin_map = {"0": "GPIO_PIN_0", "1": "GPIO_PIN_1", "2": "GPIO_PIN_2", "3": "GPIO_PIN_3", "4": "GPIO_PIN_4", "5": "GPIO_PIN_5", "6": "GPIO_PIN_6", "7": "GPIO_PIN_7", "8": "GPIO_PIN_8", "9": "GPIO_PIN_9", "10": "GPIO_PIN_10", "11": "GPIO_PIN_11", "12": "GPIO_PIN_12", "13": "GPIO_PIN_13", "14": "GPIO_PIN_14", "15": "GPIO_PIN_15"}
            
            source_code.extend([
                "    // UART初始化",
                "    rcu_periph_clock_enable(RCU_USART0);",
                f"    rcu_periph_clock_enable({rcu_map[tx_port]});",
                "    ",
                "    // 配置GPIO",
                f"    gpio_init({port_map[tx_port]}, GPIO_MODE_AF_PP, GPIO_OSPEED_50MHZ, {pin_map[tx_num]}); // TX",
                f"    gpio_init({port_map[rx_port]}, GPIO_MODE_IN_FLOATING, GPIO_OSPEED_50MHZ, {pin_map[rx_num]}); // RX",
                "    ",
                "    // 配置UART",
                "    usart_deinit(USART0);",
                f"    usart_baudrate_set(USART0, {baudrate});",
                "    usart_word_length_set(USART0, USART_WL_8BIT);",
                "    usart_stop_bit_set(USART0, USART_STB_1BIT);",
                "    usart_parity_config(USART0, USART_PM_NONE);",
                "    usart_hardware_flow_rts_config(USART0, USART_RTS_DISABLE);",
                "    usart_hardware_flow_cts_config(USART0, USART_CTS_DISABLE);",
                "    usart_receive_config(USART0, USART_RECEIVE_ENABLE);",
                "    usart_transmit_config(USART0, USART_TRANSMIT_ENABLE);",
                "    usart_enable(USART0);"
            ])
        elif peripheral == "I2C":
            source_code.extend([
                "    // I2C初始化",
                "    rcu_periph_clock_enable(RCU_I2C0);",
                "    rcu_periph_clock_enable(RCU_GPIOB);",
                "    ",
                "    // 配置GPIO",
                "    gpio_init(GPIOB, GPIO_MODE_AF_OD, GPIO_OSPEED_50MHZ, GPIO_PIN_6 | GPIO_PIN_7); // SCL, SDA",
                "    ",
                "    // 配置I2C",
                "    i2c_deinit(I2C0);",
                "    i2c_clock_config(I2C0, 100000, I2C_DTCY_2);",
                "    i2c_mode_config(I2C0, I2C_MODE_I2C);",
                "    i2c_ack_config(I2C0, I2C_ACK_ENABLE);",
                "    i2c_enable(I2C0);"
            ])
        elif peripheral == "SPI":
            source_code.extend([
                "    // SPI初始化",
                "    rcu_periph_clock_enable(RCU_SPI0);",
                "    rcu_periph_clock_enable(RCU_GPIOA);",
                "    ",
                "    // 配置GPIO",
                "    gpio_init(GPIOA, GPIO_MODE_AF_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7); // SCK, MISO, MOSI",
                "    gpio_init(GPIOA, GPIO_MODE_OUT_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_4); // NSS",
                "    ",
                "    // 配置SPI",
                "    spi_deinit(SPI0);",
                "    spi_init(SPI0, SPI_MODE_MASTER, SPI_FRAME_FORMAT_8BIT, SPI_NSS_SOFT, 16, SPI_FIRSTBIT_MSB);",
                "    spi_enable(SPI0);"
            ])
        elif peripheral == "CAN":
            source_code.extend([
                "    // CAN初始化",
                "    rcu_periph_clock_enable(RCU_CAN0);",
                "    rcu_periph_clock_enable(RCU_GPIOA);",
                "    ",
                "    // 配置GPIO",
                "    gpio_init(GPIOA, GPIO_MODE_AF_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_11 | GPIO_PIN_12); // CAN_RX, CAN_TX",
                "    ",
                "    // 配置CAN",
                "    can_deinit(CAN0);",
                "    can_struct_para_init(CAN_INIT_STRUCT);",
                "    can_init_struct.can_timing = CAN_TIMING_CONFIG_500KBPS(48000000);",
                "    can_init_struct.can_mode = CAN_MODE_NORMAL;",
                "    can_init_struct.can_sJW = CAN_SJW_1TQ;",
                "    can_init_struct.can_BS1 = CAN_BS1_8TQ;",
                "    can_init_struct.can_BS2 = CAN_BS2_7TQ;",
                "    can_init_struct.can_prescaler = 6; // 500kHz @ 48MHz",
                "    can_init(CAN0, &can_init_struct);",
                "    ",
                "    // 配置过滤器",
                "    can_struct_para_init(CAN_FILTER_STRUCT);",
                "    can_filter_struct.can_filter_number = 0;",
                "    can_filter_struct.can_filter_mode = CAN_FILTERMODE_MASK;",
                "    can_filter_struct.can_filter_scale = CAN_FILTERSCALE_32BIT;",
                "    can_filter_struct.can_filter_id_high = 0x0000;",
                "    can_filter_struct.can_filter_id_low = 0x0000;",
                "    can_filter_struct.can_filter_mask_id_high = 0x0000;",
                "    can_filter_struct.can_filter_mask_id_low = 0x0000;",
                "    can_filter_struct.can_filter_fifo_number = CAN_FIFO0;",
                "    can_filter_enable(CAN0, &can_filter_struct);"
            ])
        elif peripheral == "ADC":
            source_code.extend([
                "    // ADC初始化",
                "    rcu_periph_clock_enable(RCU_ADC0);",
                "    rcu_periph_clock_enable(RCU_GPIOA);",
                "    ",
                "    // 配置GPIO",
                "    gpio_init(GPIOA, GPIO_MODE_AIN, GPIO_OSPEED_50MHZ, GPIO_PIN_0); // ADC通道0",
                "    ",
                "    // 配置ADC",
                "    adc_deinit(ADC0);",
                "    rcu_adc_clock_config(RCU_CKADC_CKAPB2_DIV8);",
                "    adc_special_function_config(ADC0, ADC_SCAN_MODE, DISABLE);",
                "    adc_special_function_config(ADC0, ADC_CONTINUOUS_MODE, DISABLE);",
                "    adc_external_trigger_source_config(ADC0, ADC_REGULAR_CHANNEL, ADC0_1_2_EXTTRIG_REGULAR_NONE);",
                "    adc_data_alignment_config(ADC0, ADC_DATAALIGN_RIGHT);",
                "    adc_channel_length_config(ADC0, ADC_REGULAR_CHANNEL, 1);",
                "    adc_regular_channel_config(ADC0, 0, ADC_CHANNEL_0, ADC_SAMPLETIME_239POINT5);",
                "    adc_enable(ADC0);",
                "    ",
                "    // 校准ADC",
                "    adc_calibration_enable(ADC0);"
            ])
        elif peripheral == "PWM":
            source_code.extend([
                "    // PWM初始化",
                "    rcu_periph_clock_enable(RCU_TIMER1);",
                "    rcu_periph_clock_enable(RCU_GPIOA);",
                "    ",
                "    // 配置GPIO",
                "    gpio_init(GPIOA, GPIO_MODE_AF_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_8); // TIM1_CH1",
                "    ",
                "    // 配置定时器",
                "    timer_deinit(TIM1);",
                "    timer_prescaler_config(TIM1, 71, TIMER_PSC_RELOAD_NOW);",
                "    timer_autoreload_value_config(TIM1, 999);",
                "    timer_ckd_config(TIM1, TIMER_CKD_DIV1);",
                "    timer_master_mode_select(TIM1, TIMER_MASTER_MODE_DISABLE);",
                "    timer_overflow_direction_config(TIM1, TIMER_COUNTER_UP);",
                "    timer_repetition_counter_config(TIM1, 0);",
                "    ",
                "    // 配置PWM",
                "    timer_oc_parameter_struct timer_ocintpara;",
                "    timer_oc_struct_para_init(&timer_ocintpara);",
                "    timer_ocintpara.timer_oc_mode = TIMER_OC_MODE_PWM1;",
                "    timer_ocintpara.timer_output_state = TIMER_CCX_ENABLE;",
                "    timer_ocintpara.timer_output_nstate = TIMER_CCXN_DISABLE;",
                "    timer_ocintpara.timer_pulse = 500; // 50% duty cycle",
                "    timer_ocintpara.timer_oc_polarity = TIMER_OC_POLARITY_HIGH;",
                "    timer_ocintpara.timer_oc_npolarity = TIMER_OCN_POLARITY_HIGH;",
                "    timer_ocintpara.timer_oc_idle_state = TIMER_OC_IDLE_STATE_LOW;",
                "    timer_ocintpara.timer_oc_nidle_state = TIMER_OCN_IDLE_STATE_LOW;",
                "    timer_channel_output_config(TIM1, TIMER_CH_1, &timer_ocintpara);",
                "    ",
                "    // 使能输出",
                "    timer_channel_output_state_config(TIM1, TIMER_CH_1, TIMER_CCX_ENABLE);",
                "    timer_primary_output_config(TIM1, ENABLE);",
                "    ",
                "    // 启动定时器",
                "    timer_enable(TIM1);"
            ])
        elif peripheral == "TIM":
            source_code.extend([
                "    // 定时器初始化",
                "    rcu_periph_clock_enable(RCU_TIMER2);",
                "    ",
                "    // 配置定时器",
                "    timer_deinit(TIM2);",
                "    timer_prescaler_config(TIM2, 71, TIMER_PSC_RELOAD_NOW);",
                "    timer_autoreload_value_config(TIM2, 999);",
                "    timer_ckd_config(TIM2, TIMER_CKD_DIV1);",
                "    timer_master_mode_select(TIM2, TIMER_MASTER_MODE_DISABLE);",
                "    timer_overflow_direction_config(TIM2, TIMER_COUNTER_UP);",
                "    timer_repetition_counter_config(TIM2, 0);",
                "    ",
                "    // 配置中断",
                "    nvic_irq_enable(TIMER2_IRQn, 0, 0);",
                "    timer_interrupt_enable(TIM2, TIMER_INT_UP);",
                "    ",
                "    // 启动定时器",
                "    timer_enable(TIM2);"
            ])
        
        source_code.append("}")
        
        # 添加UART操作函数实现
        if peripheral == "UART":
            if is_cpp:
                source_code.extend([
                    "",
                    "void UARTDriver::send_byte(uint8_t byte) {",
                    "    // 发送一个字节",
                    "    while (usart_flag_get(USART0, USART_FLAG_TBE) == RESET);",
                    "    usart_data_transmit(USART0, byte);",
                    "}",
                    "",
                    "void UARTDriver::send_string(const char* str) {",
                    "    // 发送字符串",
                    "    while (*str) {",
                    "        send_byte(*str++);",
                    "    }",
                    "}",
                    "",
                    "uint8_t UARTDriver::receive_byte() {",
                    "    // 接收一个字节",
                    "    while (usart_flag_get(USART0, USART_FLAG_RBNE) == RESET);",
                    "    return usart_data_receive(USART0);",
                    "}",
                    "",
                    "void UARTDriver::receive_string(char* buffer, uint16_t length) {",
                    "    // 接收字符串",
                    "    uint16_t i = 0;",
                    "    while (i < length - 1) {",
                    "        buffer[i] = receive_byte();",
                    "        if (buffer[i] == '\\0') break;",
                    "        i++;",
                    "    }",
                    "    buffer[i] = '\\0';",
                    "}",
                    "",
                    "void UARTDriver::config_interrupt() {",
                    "    // 配置UART中断",
                    "    nvic_irq_enable(USART0_IRQn, 0, 0);",
                    "    usart_interrupt_enable(USART0, USART_INT_RBNE);",
                    "}"
                ])
            else:
                source_code.extend([
                    "",
                    "void UART_send_byte(uint8_t byte) {",
                    "    // 发送一个字节",
                    "    while (usart_flag_get(USART0, USART_FLAG_TBE) == RESET);",
                    "    usart_data_transmit(USART0, byte);",
                    "}",
                    "",
                    "void UART_send_string(const char* str) {",
                    "    // 发送字符串",
                    "    while (*str) {",
                    "        UART_send_byte(*str++);",
                    "    }",
                    "}",
                    "",
                    "uint8_t UART_receive_byte(void) {",
                    "    // 接收一个字节",
                    "    while (usart_flag_get(USART0, USART_FLAG_RBNE) == RESET);",
                    "    return usart_data_receive(USART0);",
                    "}",
                    "",
                    "void UART_receive_string(char* buffer, uint16_t length) {",
                    "    // 接收字符串",
                    "    uint16_t i = 0;",
                    "    while (i < length - 1) {",
                    "        buffer[i] = UART_receive_byte();",
                    "        if (buffer[i] == '\\0') break;",
                    "        i++;",
                    "    }",
                    "    buffer[i] = '\\0';",
                    "}",
                    "",
                    "void UART_config_interrupt(void) {",
                    "    // 配置UART中断",
                    "    nvic_irq_enable(USART0_IRQn, 0, 0);",
                    "    usart_interrupt_enable(USART0, USART_INT_RBNE);",
                    "}"
                ])
        # 添加I2C操作函数实现
        elif peripheral == "I2C":
            if is_cpp:
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 发送I2C起始信号",
                    " * @retval None",
                    " */",
                    "void I2CDriver::start() {",
                    "    // 发送I2C起始信号",
                    "    i2c_start_on_bus(I2C0);",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_SBSEND) == RESET);",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C停止信号",
                    " * @retval None",
                    " */",
                    "void I2CDriver::stop() {",
                    "    // 发送I2C停止信号",
                    "    i2c_stop_on_bus(I2C0);",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_STOPF) == RESET);",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C应答信号",
                    " * @retval None",
                    " */",
                    "void I2CDriver::send_ack() {",
                    "    // 发送I2C应答信号",
                    "    i2c_ack_config(I2C0, I2C_ACK_ENABLE);",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C非应答信号",
                    " * @retval None",
                    " */",
                    "void I2CDriver::send_nack() {",
                    "    // 发送I2C非应答信号",
                    "    i2c_ack_config(I2C0, I2C_ACK_DISABLE);",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取一个字节数据",
                    " * @retval uint8_t 读取到的字节数据",
                    " */",
                    "uint8_t I2CDriver::read_byte() {",
                    "    // 读取一个字节数据",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_RBNE) == RESET);",
                    "    return i2c_data_receive(I2C0);",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入一个字节数据",
                    " * @param byte 要写入的字节数据",
                    " * @retval None",
                    " */",
                    "void I2CDriver::write_byte(uint8_t byte) {",
                    "    // 写入一个字节数据",
                    "    i2c_data_transmit(I2C0, byte);",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_TBE) == RESET);",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @retval uint8_t 读取到的寄存器值",
                    " */",
                    "uint8_t I2CDriver::read_register(uint8_t slave_addr, uint8_t reg_addr) {",
                    "    // 读取从设备寄存器值",
                    "    start();",
                    "    write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_ADDSEND) == RESET);",
                    "    i2c_flag_clear(I2C0, I2C_FLAG_ADDSEND);",
                    "    ",
                    "    write_byte(reg_addr); // 发送寄存器地址",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_TBE) == RESET);",
                    "    ",
                    "    start(); // 重复起始信号",
                    "    write_byte((slave_addr << 1) | 1); // 发送从设备地址，读模式",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_ADDSEND) == RESET);",
                    "    i2c_flag_clear(I2C0, I2C_FLAG_ADDSEND);",
                    "    ",
                    "    send_nack(); // 发送非应答",
                    "    uint8_t data = read_byte();",
                    "    stop();",
                    "    ",
                    "    return data;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 要写入的数据",
                    " * @retval None",
                    " */",
                    "void I2CDriver::write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                    "    // 写入从设备寄存器值",
                    "    start();",
                    "    write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_ADDSEND) == RESET);",
                    "    i2c_flag_clear(I2C0, I2C_FLAG_ADDSEND);",
                    "    ",
                    "    write_byte(reg_addr); // 发送寄存器地址",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_TBE) == RESET);",
                    "    ",
                    "    write_byte(data); // 发送数据",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_TBE) == RESET);",
                    "    ",
                    "    stop();",
                    "}"
                ])
            else:
                source_code.extend([
                    "",
                    "/**",
                    " * @brief 发送I2C起始信号",
                    " * @retval None",
                    " */",
                    "void I2C_start(void) {",
                    "    // 发送I2C起始信号",
                    "    i2c_start_on_bus(I2C0);",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_SBSEND) == RESET);",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C停止信号",
                    " * @retval None",
                    " */",
                    "void I2C_stop(void) {",
                    "    // 发送I2C停止信号",
                    "    i2c_stop_on_bus(I2C0);",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_STOPF) == RESET);",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C应答信号",
                    " * @retval None",
                    " */",
                    "void I2C_send_ack(void) {",
                    "    // 发送I2C应答信号",
                    "    i2c_ack_config(I2C0, I2C_ACK_ENABLE);",
                    "}",
                    "",
                    "/**",
                    " * @brief 发送I2C非应答信号",
                    " * @retval None",
                    " */",
                    "void I2C_send_nack(void) {",
                    "    // 发送I2C非应答信号",
                    "    i2c_ack_config(I2C0, I2C_ACK_DISABLE);",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取一个字节数据",
                    " * @retval uint8_t 读取到的字节数据",
                    " */",
                    "uint8_t I2C_read_byte(void) {",
                    "    // 读取一个字节数据",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_RBNE) == RESET);",
                    "    return i2c_data_receive(I2C0);",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入一个字节数据",
                    " * @param byte 要写入的字节数据",
                    " * @retval None",
                    " */",
                    "void I2C_write_byte(uint8_t byte) {",
                    "    // 写入一个字节数据",
                    "    i2c_data_transmit(I2C0, byte);",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_TBE) == RESET);",
                    "}",
                    "",
                    "/**",
                    " * @brief 读取从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @retval uint8_t 读取到的寄存器值",
                    " */",
                    "uint8_t I2C_read_register(uint8_t slave_addr, uint8_t reg_addr) {",
                    "    // 读取从设备寄存器值",
                    "    I2C_start();",
                    "    I2C_write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_ADDSEND) == RESET);",
                    "    i2c_flag_clear(I2C0, I2C_FLAG_ADDSEND);",
                    "    ",
                    "    I2C_write_byte(reg_addr); // 发送寄存器地址",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_TBE) == RESET);",
                    "    ",
                    "    I2C_start(); // 重复起始信号",
                    "    I2C_write_byte((slave_addr << 1) | 1); // 发送从设备地址，读模式",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_ADDSEND) == RESET);",
                    "    i2c_flag_clear(I2C0, I2C_FLAG_ADDSEND);",
                    "    ",
                    "    I2C_send_nack(); // 发送非应答",
                    "    uint8_t data = I2C_read_byte();",
                    "    I2C_stop();",
                    "    ",
                    "    return data;",
                    "}",
                    "",
                    "/**",
                    " * @brief 写入从设备寄存器值",
                    " * @param slave_addr 从设备地址",
                    " * @param reg_addr 寄存器地址",
                    " * @param data 要写入的数据",
                    " * @retval None",
                    " */",
                    "void I2C_write_register(uint8_t slave_addr, uint8_t reg_addr, uint8_t data) {",
                    "    // 写入从设备寄存器值",
                    "    I2C_start();",
                    "    I2C_write_byte((slave_addr << 1) | 0); // 发送从设备地址，写模式",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_ADDSEND) == RESET);",
                    "    i2c_flag_clear(I2C0, I2C_FLAG_ADDSEND);",
                    "    ",
                    "    I2C_write_byte(reg_addr); // 发送寄存器地址",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_TBE) == RESET);",
                    "    ",
                    "    I2C_write_byte(data); // 发送数据",
                    "    while (i2c_flag_get(I2C0, I2C_FLAG_TBE) == RESET);",
                    "    ",
                    "    I2C_stop();",
                    "}"
                ])
        
        # 添加中断处理函数（如果需要）
        if peripheral == "TIM":
            source_code.extend([
                "",
                "// 定时器中断处理函数",
                "void TIMER2_IRQHandler(void) {",
                "    if(timer_flag_get(TIMER2, TIMER_FLAG_UP)) {",
                "        // 处理定时器中断",
                "        ",
                "        // 清除中断标志位",
                "        timer_flag_clear(TIMER2, TIMER_FLAG_UP);",
                "    }",
                "}"
            ])
        
        return "\n".join(header_code), "\n".join(source_code)
    
    def generate_hc32_code(self, peripheral, language, params):
        """生成HC32代码"""
        header_code = []
        source_code = []
        is_cpp = language == "C++语言"
        
        # 头文件
        if is_cpp:
            header_code.append('#include <cstdint>')
        else:
            header_code.append('#include <stdint.h>')
        header_code.append('#include "hc32l136.h"')
        
        header_code.append("")
        
        # 函数声明
        if is_cpp:
            header_code.append("class " + peripheral + "Driver {")
            header_code.append("public:")
            header_code.append("    static void init();")
            if peripheral == "UART":
                header_code.extend([
                    "    static void send_byte(uint8_t byte);",
                    "    static void send_string(const char* str);",
                    "    static uint8_t receive_byte();",
                    "    static void receive_string(char* buffer, uint16_t length);",
                    "    static void config_interrupt();"
                ])
            header_code.append("};")
        else:
            header_code.append("void " + peripheral + "_init(void);")
            if peripheral == "UART":
                header_code.extend([
                    "void UART_send_byte(uint8_t byte);",
                    "void UART_send_string(const char* str);",
                    "uint8_t UART_receive_byte(void);",
                    "void UART_receive_string(char* buffer, uint16_t length);",
                    "void UART_config_interrupt(void);"
                ])
        
        # 源文件包含头文件
        source_code.extend([
            f"#include \"{peripheral.lower()}_driver.h\""
        ])
        
        # 函数实现
        if is_cpp:
            source_code.append("void " + peripheral + "Driver::init() {")
        else:
            source_code.append("void " + peripheral + "_init(void) {")
        
        # 根据外设生成初始化代码
        if peripheral == "GPIO":
            pin = params.get('pin', 'PA0')
            mode = params.get('mode', '输出')
            level = params.get('level', '低')
            
            # 解析引脚
            port = pin[1] if pin[0] == 'P' else pin[0]
            pin_num = int(pin[2:]) if pin[0] == 'P' else int(pin[1:])
            
            port_map = {"A": "GpioPortA", "B": "GpioPortB", "C": "GpioPortC", "D": "GpioPortD"}
            pin_map = {0: "GpioPin0", 1: "GpioPin1", 2: "GpioPin2", 3: "GpioPin3", 4: "GpioPin4", 5: "GpioPin5", 6: "GpioPin6", 7: "GpioPin7", 8: "GpioPin8", 9: "GpioPin9", 10: "GpioPin10", 11: "GpioPin11", 12: "GpioPin12", 13: "GpioPin13", 14: "GpioPin14", 15: "GpioPin15"}
            
            source_code.extend([
                "    // GPIO初始化",
                "    stc_gpio_cfg_t stcGpioCfg;",
                "    ",
                "    // 使能GPIO时钟",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralGpio, TRUE);",
                "    ",
                "    // 配置GPIO",
                "    Gpio_StructInit(&stcGpioCfg);",
                f"    stcGpioCfg.enDir = {'GpioDirOut' if mode == '输出' else 'GpioDirIn'}; // {mode}模式",
                f"    Gpio_Init({port_map[port]}, {pin_map[pin_num]}, &stcGpioCfg); // {pin}"
            ])
            
            if mode == "输出":
                source_code.append(f"    Gpio_Write({port_map[port]}, {pin_map[pin_num]}, {'TRUE' if level == '高' else 'FALSE'}); // 初始{level}电平")
        elif peripheral == "UART":
            source_code.extend([
                "    // UART初始化",
                "    stc_uart_cfg_t stcUartCfg;",
                "    stc_gpio_cfg_t stcGpioCfg;",
                "    ",
                "    // 使能时钟",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralGpio, TRUE);",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralUart0, TRUE);",
                "    ",
                "    // 配置GPIO",
                "    Gpio_StructInit(&stcGpioCfg);",
                "    stcGpioCfg.enDir = GpioDirOut; // 输出模式",
                "    stcGpioCfg.enPu = GpioPuEnable; // 上拉使能",
                "    Gpio_Init(GpioPortA, GpioPin9, &stcGpioCfg); // TX",
                "    ",
                "    stcGpioCfg.enDir = GpioDirIn; // 输入模式",
                "    Gpio_Init(GpioPortA, GpioPin10, &stcGpioCfg); // RX",
                "    ",
                "    // 配置UART",
                "    Uart_StructInit(&stcUartCfg);",
                "    stcUartCfg.enBaudrate = 115200; // 波特率",
                "    stcUartCfg.enDataBits = UartDataBits8; // 8位数据",
                "    stcUartCfg.enStopBits = UartStopBits1; // 1位停止位",
                "    stcUartCfg.enParity = UartParityNone; // 无校验",
                "    Uart_Init(M0P_UART0, &stcUartCfg);",
                "    ",
                "    // 使能UART",
                "    Uart_Enable(M0P_UART0);"
            ])
        elif peripheral == "I2C":
            source_code.extend([
                "    // I2C初始化",
                "    stc_i2c_cfg_t stcI2cCfg;",
                "    stc_gpio_cfg_t stcGpioCfg;",
                "    ",
                "    // 使能时钟",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralGpio, TRUE);",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralI2c0, TRUE);",
                "    ",
                "    // 配置GPIO",
                "    Gpio_StructInit(&stcGpioCfg);",
                "    stcGpioCfg.enDir = GpioDirOut; // 输出模式",
                "    stcGpioCfg.enOD = GpioOdEnable; // 开漏输出",
                "    stcGpioCfg.enPu = GpioPuEnable; // 上拉使能",
                "    Gpio_Init(GpioPortB, GpioPin6, &stcGpioCfg); // SCL",
                "    Gpio_Init(GpioPortB, GpioPin7, &stcGpioCfg); // SDA",
                "    ",
                "    // 配置I2C",
                "    I2c_StructInit(&stcI2cCfg);",
                "    stcI2cCfg.u32Baud = 100000; // 100kHz",
                "    I2c_Init(M0P_I2C0, &stcI2cCfg);",
                "    ",
                "    // 使能I2C",
                "    I2c_Enable(M0P_I2C0);"
            ])
        elif peripheral == "SPI":
            source_code.extend([
                "    // SPI初始化",
                "    stc_spi_cfg_t stcSpiCfg;",
                "    stc_gpio_cfg_t stcGpioCfg;",
                "    ",
                "    // 使能时钟",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralGpio, TRUE);",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralSpi, TRUE);",
                "    ",
                "    // 配置GPIO",
                "    Gpio_StructInit(&stcGpioCfg);",
                "    stcGpioCfg.enDir = GpioDirOut; // 输出模式",
                "    stcGpioCfg.enPu = GpioPuEnable; // 上拉使能",
                "    Gpio_Init(GpioPortA, GpioPin5, &stcGpioCfg); // SCK",
                "    Gpio_Init(GpioPortA, GpioPin7, &stcGpioCfg); // MOSI",
                "    ",
                "    stcGpioCfg.enDir = GpioDirIn; // 输入模式",
                "    Gpio_Init(GpioPortA, GpioPin6, &stcGpioCfg); // MISO",
                "    ",
                "    // 配置SPI",
                "    Spi_StructInit(&stcSpiCfg);",
                "    stcSpiCfg.enSpiMode = SpiMskMaster; // 主模式",
                "    stcSpiCfg.enClkDiv = SpiClkDiv8; // 时钟分频",
                "    stcSpiCfg.enCPOL = SpiMskCPOL_High; // 时钟极性",
                "    stcSpiCfg.enCPHA = SpiMskCPHA_2Edge; // 时钟相位",
                "    Spi_Init(M0P_SPI, &stcSpiCfg);",
                "    ",
                "    // 使能SPI",
                "    Spi_Enable(M0P_SPI);"
            ])
        elif peripheral == "CAN":
            source_code.extend([
                "    // CAN初始化",
                "    // HC32L136不支持CAN接口"
            ])
        elif peripheral == "ADC":
            source_code.extend([
                "    // ADC初始化",
                "    stc_adc_cfg_t stcAdcCfg;",
                "    stc_gpio_cfg_t stcGpioCfg;",
                "    ",
                "    // 使能时钟",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralGpio, TRUE);",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralAdc, TRUE);",
                "    ",
                "    // 配置GPIO",
                "    Gpio_StructInit(&stcGpioCfg);",
                "    stcGpioCfg.enDir = GpioDirIn; // 输入模式",
                "    Gpio_Init(GpioPortA, GpioPin0, &stcGpioCfg); // ADC通道0",
                "    ",
                "    // 配置ADC",
                "    Adc_StructInit(&stcAdcCfg);",
                "    stcAdcCfg.enAdcMode = AdcMskSglMode; // 单次模式",
                "    stcAdcCfg.enAdcClkDiv = AdcMskClkDiv16; // 时钟分频",
                "    Adc_Init(&stcAdcCfg);",
                "    ",
                "    // 使能ADC",
                "    Adc_Enable();"
            ])
        elif peripheral == "PWM":
            source_code.extend([
                "    // PWM初始化",
                "    stc_bt_cfg_t stcBtCfg;",
                "    stc_gpio_cfg_t stcGpioCfg;",
                "    ",
                "    // 使能时钟",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralGpio, TRUE);",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralBt, TRUE);",
                "    ",
                "    // 配置GPIO",
                "    Gpio_StructInit(&stcGpioCfg);",
                "    stcGpioCfg.enDir = GpioDirOut; // 输出模式",
                "    stcGpioCfg.enPu = GpioPuEnable; // 上拉使能",
                "    Gpio_Init(GpioPortA, GpioPin1, &stcGpioCfg); // BT0_CHA",
                "    ",
                "    // 配置BT",
                "    Bt_StructInit(&stcBtCfg);",
                "    stcBtCfg.enMode = BtMskModeTimer; // 定时器模式",
                "    stcBtCfg.enCntMode = BtMskCntModeSawtooth; // 锯齿波计数",
                "    stcBtCfg.enPwmMode = BtMskPwmMode2; // PWM模式2",
                "    stcBtCfg.u16CmpValA = 500; // 比较值A",
                "    stcBtCfg.u16ArrVal = 1000; // 自动重装载值",
                "    Bt_Init(M0P_BT0, &stcBtCfg);",
                "    ",
                "    // 使能BT",
                "    Bt_Enable(M0P_BT0);"
            ])
        elif peripheral == "TIM":
            source_code.extend([
                "    // 定时器初始化",
                "    stc_bt_cfg_t stcBtCfg;",
                "    ",
                "    // 使能时钟",
                "    Sysctrl_SetPeripheralGate(SysctrlPeripheralBt, TRUE);",
                "    ",
                "    // 配置BT",
                "    Bt_StructInit(&stcBtCfg);",
                "    stcBtCfg.enMode = BtMskModeTimer; // 定时器模式",
                "    stcBtCfg.enCntMode = BtMskCntModeSawtooth; // 锯齿波计数",
                "    stcBtCfg.u16ArrVal = 1000; // 自动重装载值",
                "    Bt_Init(M0P_BT0, &stcBtCfg);",
                "    ",
                "    // 配置中断",
                "    EnableNvic(BT0_IRQn, IrqLevel3, TRUE);",
                "    Bt_IntCmd(M0P_BT0, BtUevIrq, TRUE);",
                "    ",
                "    // 使能BT",
                "    Bt_Enable(M0P_BT0);"
            ])
        
        source_code.append("}")
        
        # 添加UART操作函数实现
        if peripheral == "UART":
            if is_cpp:
                source_code.extend([
                    "",
                    "void UARTDriver::send_byte(uint8_t byte) {",
                    "    // 发送一个字节",
                    "    Uart_SendData(M0P_UART0, byte);",
                    "    while (!Uart_GetStatus(M0P_UART0, UartTxEmpty));",
                    "}",
                    "",
                    "void UARTDriver::send_string(const char* str) {",
                    "    // 发送字符串",
                    "    while (*str) {",
                    "        send_byte(*str++);",
                    "    }",
                    "}",
                    "",
                    "uint8_t UARTDriver::receive_byte() {",
                    "    // 接收一个字节",
                    "    while (!Uart_GetStatus(M0P_UART0, UartRxFull));",
                    "    return Uart_ReceiveData(M0P_UART0);",
                    "}",
                    "",
                    "void UARTDriver::receive_string(char* buffer, uint16_t length) {",
                    "    // 接收字符串",
                    "    uint16_t i = 0;",
                    "    while (i < length - 1) {",
                    "        buffer[i] = receive_byte();",
                    "        if (buffer[i] == '\\0') break;",
                    "        i++;",
                    "    }",
                    "    buffer[i] = '\\0';",
                    "}",
                    "",
                    "void UARTDriver::config_interrupt() {",
                    "    // 配置UART中断",
                    "    EnableNvic(UART0_IRQn, IrqLevel3, TRUE);",
                    "    Uart_IntCmd(M0P_UART0, UartRxIrq, TRUE);",
                    "}"
                ])
            else:
                source_code.extend([
                    "",
                    "void UART_send_byte(uint8_t byte) {",
                    "    // 发送一个字节",
                    "    Uart_SendData(M0P_UART0, byte);",
                    "    while (!Uart_GetStatus(M0P_UART0, UartTxEmpty));",
                    "}",
                    "",
                    "void UART_send_string(const char* str) {",
                    "    // 发送字符串",
                    "    while (*str) {",
                    "        UART_send_byte(*str++);",
                    "    }",
                    "}",
                    "",
                    "uint8_t UART_receive_byte(void) {",
                    "    // 接收一个字节",
                    "    while (!Uart_GetStatus(M0P_UART0, UartRxFull));",
                    "    return Uart_ReceiveData(M0P_UART0);",
                    "}",
                    "",
                    "void UART_receive_string(char* buffer, uint16_t length) {",
                    "    // 接收字符串",
                    "    uint16_t i = 0;",
                    "    while (i < length - 1) {",
                    "        buffer[i] = UART_receive_byte();",
                    "        if (buffer[i] == '\\0') break;",
                    "        i++;",
                    "    }",
                    "    buffer[i] = '\\0';",
                    "}",
                    "",
                    "void UART_config_interrupt(void) {",
                    "    // 配置UART中断",
                    "    EnableNvic(UART0_IRQn, IrqLevel3, TRUE);",
                    "    Uart_IntCmd(M0P_UART0, UartRxIrq, TRUE);",
                    "}"
                ])
        
        # 添加中断处理函数（如果需要）
        if peripheral == "TIM":
            source_code.extend([
                "",
                "// 定时器中断处理函数",
                "void BT0_IRQHandler(void) {",
                "    if(Bt_GetIntFlag(M0P_BT0, BtUevIrq)) {",
                "        // 处理定时器中断",
                "        ",
                "        // 清除中断标志位",
                "        Bt_ClearIntFlag(M0P_BT0, BtUevIrq);",
                "    }",
                "}"
            ])
        
        return "\n".join(header_code), "\n".join(source_code)
    
    def generate_same70_code(self, peripheral, language, lib_type, xtal, params):
        """生成ATSAME70代码"""
        header_code = []
        source_code = []
        is_cpp = language == "C++语言"
        
        # 头文件
        if is_cpp:
            header_code.append('#include <cstdint>')
        else:
            header_code.append('#include <stdint.h>')
        header_code.append('#include "sam.h"')
        
        header_code.append("")
        
        # 函数声明
        if is_cpp:
            header_code.append("class " + peripheral + "Driver {")
            header_code.append("public:")
            header_code.append("    static void init();")
            if peripheral == "UART":
                header_code.extend([
                    "    static void send_byte(uint8_t byte);",
                    "    static void send_string(const char* str);",
                    "    static uint8_t receive_byte();",
                    "    static void receive_string(char* buffer, uint16_t length);",
                    "    static void config_interrupt();"
                ])
            header_code.append("};")
        else:
            header_code.append("void " + peripheral + "_init(void);")
            if peripheral == "UART":
                header_code.extend([
                    "void UART_send_byte(uint8_t byte);",
                    "void UART_send_string(const char* str);",
                    "uint8_t UART_receive_byte(void);",
                    "void UART_receive_string(char* buffer, uint16_t length);",
                    "void UART_config_interrupt(void);"
                ])
        
        # 源文件包含头文件
        source_code.extend([
            f"#include \"{peripheral.lower()}_driver.h\""
        ])
        
        # 函数实现
        if is_cpp:
            source_code.append("void " + peripheral + "Driver::init() {")
        else:
            source_code.append("void " + peripheral + "_init(void) {")
        
        # 根据外设生成初始化代码
        if peripheral == "GPIO":
            pin = params.get('pin', 'PA0')
            mode = params.get('mode', '输出')
            level = params.get('level', '低')
            
            # 解析引脚
            port = pin[1] if pin[0] == 'P' else pin[0]
            pin_num = int(pin[2:]) if pin[0] == 'P' else int(pin[1:])
            
            port_map = {"A": "PIOA", "B": "PIOB", "C": "PIOC", "D": "PIOD"}
            
            source_code.extend([
                "    // GPIO初始化",
                f"    PMC->PMC_PCER0 |= PMC_PCER0_PID11; // 使能PIO{port}时钟",
                "    ",
                f"    // 配置{pin}为{mode}",
                f"    {port_map[port]}->PIO_PER |= (1 << {pin_num}); // 使能引脚",
            ])
            
            if mode == "输出":
                source_code.extend([
                    f"    {port_map[port]}->PIO_OER |= (1 << {pin_num}); // 输出模式",
                    f"    {port_map[port]}->PIO_{'SODR' if level == '高' else 'CODR'} |= (1 << {pin_num}); // 初始{level}电平"
                ])
            else:
                source_code.append(f"    {port_map[port]}->PIO_ODR &= ~(1 << {pin_num}); // 输入模式")
        elif peripheral == "UART":
            baudrate = params.get('baudrate', 9600)
            
            source_code.extend([
                "    // UART初始化",
                "    PMC->PMC_PCER0 |= PMC_PCER0_PID8; // 使能UART0时钟",
                "    PMC->PMC_PCER0 |= PMC_PCER0_PID11; // 使能PIOA时钟",
                "    ",
                "    // 配置GPIO",
                "    PIOA->PIO_PER |= PIO_PA9 | PIO_PA10; // 使能引脚",
                "    PIOA->PIO_ABCDSR[0] &= ~(PIO_PA9 | PIO_PA10); // 选择A功能",
                "    PIOA->PIO_ABCDSR[1] &= ~(PIO_PA9 | PIO_PA10);",
                "    ",
                "    // 配置UART",
                "    UART0->UART_CR = UART_CR_RSTRX | UART_CR_RSTTX | UART_CR_RXEN | UART_CR_TXEN; // 复位并使能收发",
                "    UART0->UART_MR = UART_MR_CHMODE_NORMAL | UART_MR_PAR_NO; // 正常模式，无校验",
                f"    UART0->UART_BRGR = (F_CPU / (16 * {baudrate})) - 1; // 波特率设置",
                "    ",
                "    // 使能UART",
                "    UART0->UART_CR = UART_CR_RXEN | UART_CR_TXEN;"
            ])
        else:
            source_code.extend([
                f"    // {peripheral}初始化",
                "    // 暂不支持该外设",
                "    // 请参考ATSAME70数据手册和SDK示例"
            ])
        
        source_code.append("}")
        
        # 添加UART操作函数实现
        if peripheral == "UART":
            if is_cpp:
                source_code.extend([
                    "",
                    "void UARTDriver::send_byte(uint8_t byte) {",
                    "    // 发送一个字节",
                    "    while (!(UART0->UART_SR & UART_SR_TXRDY));",
                    "    UART0->UART_THR = byte;",
                    "}",
                    "",
                    "void UARTDriver::send_string(const char* str) {",
                    "    // 发送字符串",
                    "    while (*str) {",
                    "        send_byte(*str++);",
                    "    }",
                    "}",
                    "",
                    "uint8_t UARTDriver::receive_byte() {",
                    "    // 接收一个字节",
                    "    while (!(UART0->UART_SR & UART_SR_RXRDY));",
                    "    return UART0->UART_RHR;",
                    "}",
                    "",
                    "void UARTDriver::receive_string(char* buffer, uint16_t length) {",
                    "    // 接收字符串",
                    "    uint16_t i = 0;",
                    "    while (i < length - 1) {",
                    "        buffer[i] = receive_byte();",
                    "        if (buffer[i] == '\\0') break;",
                    "        i++;",
                    "    }",
                    "    buffer[i] = '\\0';",
                    "}",
                    "",
                    "void UARTDriver::config_interrupt() {",
                    "    // 配置UART中断",
                    "    NVIC_EnableIRQ(UART0_IRQn);",
                    "    UART0->UART_IER = UART_IER_RXRDY;",
                    "}"
                ])
            else:
                source_code.extend([
                    "",
                    "void UART_send_byte(uint8_t byte) {",
                    "    // 发送一个字节",
                    "    while (!(UART0->UART_SR & UART_SR_TXRDY));",
                    "    UART0->UART_THR = byte;",
                    "}",
                    "",
                    "void UART_send_string(const char* str) {",
                    "    // 发送字符串",
                    "    while (*str) {",
                    "        UART_send_byte(*str++);",
                    "    }",
                    "}",
                    "",
                    "uint8_t UART_receive_byte(void) {",
                    "    // 接收一个字节",
                    "    while (!(UART0->UART_SR & UART_SR_RXRDY));",
                    "    return UART0->UART_RHR;",
                    "}",
                    "",
                    "void UART_receive_string(char* buffer, uint16_t length) {",
                    "    // 接收字符串",
                    "    uint16_t i = 0;",
                    "    while (i < length - 1) {",
                    "        buffer[i] = UART_receive_byte();",
                    "        if (buffer[i] == '\\0') break;",
                    "        i++;",
                    "    }",
                    "    buffer[i] = '\\0';",
                    "}",
                    "",
                    "void UART_config_interrupt(void) {",
                    "    // 配置UART中断",
                    "    NVIC_EnableIRQ(UART0_IRQn);",
                    "    UART0->UART_IER = UART_IER_RXRDY;",
                    "}"
                ])
        
        return "\n".join(header_code), "\n".join(source_code)
    
    def highlight_syntax(self):
        """增强的语法高亮"""
        # 处理header_text和source_text两个文本框
        for text_widget in [self.header_text, self.source_text]:
            # 清除所有标签
            text_widget.tag_remove("keyword", 1.0, tk.END)
            text_widget.tag_remove("comment", 1.0, tk.END)
            text_widget.tag_remove("string", 1.0, tk.END)
            text_widget.tag_remove("function", 1.0, tk.END)
            text_widget.tag_remove("preprocessor", 1.0, tk.END)
            text_widget.tag_remove("number", 1.0, tk.END)
            
            # 配置标签颜色和样式
            text_widget.tag_config("keyword", foreground="#0000ff", font=('Courier', 10, 'bold'))
            text_widget.tag_config("comment", foreground="#008000", font=('Courier', 10, 'italic'))
            text_widget.tag_config("string", foreground="#a31515")
            text_widget.tag_config("function", foreground="#795e26", font=('Courier', 10, 'bold'))
            text_widget.tag_config("preprocessor", foreground="#0000ff", font=('Courier', 10, 'bold'))
            text_widget.tag_config("number", foreground="#098658")
            
            # 关键字列表
            keywords = [
                "void", "int", "char", "float", "double", "unsigned", "signed",
                "struct", "class", "public", "private", "protected", "static",
                "const", "volatile", "if", "else", "for", "while", "do",
                "switch", "case", "default", "break", "continue", "return",
                "typedef", "enum", "extern", "short", "long", "bool", "true", "false"
            ]
            
            # 高亮预处理器指令
            start = 1.0
            while True:
                pos = text_widget.search(r"#\w+", start, stopindex=tk.END, regexp=True)
                if not pos:
                    break
                # 找到指令结束位置（行尾）
                end = pos + " lineend"
                text_widget.tag_add("preprocessor", pos, end)
                start = end
            
            # 高亮关键字
            for keyword in keywords:
                pattern = r"\b" + keyword + r"\b"
                start = 1.0
                while True:
                    pos = text_widget.search(pattern, start, stopindex=tk.END, regexp=True)
                    if not pos:
                        break
                    end = pos + f"+{len(keyword)}c"
                    text_widget.tag_add("keyword", pos, end)
                    start = end
            
            # 高亮函数定义
            start = 1.0
            while True:
                pos = text_widget.search(r"\b\w+\s+\w+\s*\(", start, stopindex=tk.END, regexp=True)
                if not pos:
                    break
                # 找到函数名结束位置
                match = re.search(r"\b\w+\s+(\w+)\s*\(", text_widget.get(pos, pos + "+50c"))
                if match:
                    func_name = match.group(1)
                    end = pos + f"+{len(match.group(0)) - len(func_name)}c"
                    text_widget.tag_add("function", pos, end)
                start = pos + "+10c"  # 跳过当前匹配，继续搜索
            
            # 高亮注释
            start = 1.0
            while True:
                pos = text_widget.search(r"//.*$", start, stopindex=tk.END, regexp=True)
                if not pos:
                    break
                end = pos + " lineend"
                text_widget.tag_add("comment", pos, end)
                start = end
            
            # 高亮多行注释
            start = 1.0
            while True:
                pos = text_widget.search(r"/\*", start, stopindex=tk.END, regexp=True)
                if not pos:
                    break
                # 找到注释结束位置
                end_pos = text_widget.search(r"\*/", pos, stopindex=tk.END, regexp=True)
                if end_pos:
                    end = end_pos + "+2c"  # 包含 */
                    text_widget.tag_add("comment", pos, end)
                    start = end
                else:
                    start = pos + "+1c"
            
            # 高亮字符串
            start = 1.0
            while True:
                pos = text_widget.search(r'"[^"\\\\]*(\\\\.[^"\\\\]*)*"', start, stopindex=tk.END, regexp=True)
                if not pos:
                    break
                # 找到字符串结束位置
                # 计算字符串长度
                match = re.search(r'"[^"\\]*(\\.[^"\\]*)*"', text_widget.get(pos, pos + "+100c"))
                if match:
                    end = pos + f"+{len(match.group(0))}c"
                    text_widget.tag_add("string", pos, end)
                    start = end
                else:
                    start = pos + "+1c"
            
            # 高亮数字
            start = 1.0
            while True:
                pos = text_widget.search(r"\b\d+(\.\d+)?\b", start, stopindex=tk.END, regexp=True)
                if not pos:
                    break
                # 找到数字结束位置
                match = re.search(r"\b\d+(\.\d+)?\b", text_widget.get(pos, pos + "+20c"))
                if match:
                    end = pos + f"+{len(match.group(0))}c"
                    text_widget.tag_add("number", pos, end)
                    start = end
                else:
                    start = pos + "+1c"

    def update_line_numbers(self, event):
        """更新行号显示"""
        # 更新头文件行号
        self.header_line_numbers.config(state=tk.NORMAL)
        self.header_line_numbers.delete(1.0, tk.END)
        line_count = int(self.header_text.index('end-1c').split('.')[0])
        for i in range(1, line_count + 1):
            self.header_line_numbers.insert(tk.END, f"{i}\n")
        self.header_line_numbers.config(state=tk.DISABLED)
        
        # 更新源文件行号
        self.source_line_numbers.config(state=tk.NORMAL)
        self.source_line_numbers.delete(1.0, tk.END)
        line_count = int(self.source_text.index('end-1c').split('.')[0])
        for i in range(1, line_count + 1):
            self.source_line_numbers.insert(tk.END, f"{i}\n")
        self.source_line_numbers.config(state=tk.DISABLED)
    
    def sync_scroll(self, event):
        """同步滚动行号和代码"""
        # 同步头文件滚动
        if event.widget == self.header_text:
            self.header_line_numbers.yview_moveto(self.header_text.yview()[0])
        # 同步源文件滚动
        elif event.widget == self.source_text:
            self.source_line_numbers.yview_moveto(self.source_text.yview()[0])

    def copy_code(self):
        """复制代码到剪贴板"""
        # 获取头文件和源文件内容
        header_code = self.header_text.get(1.0, tk.END).strip()
        source_code = self.source_text.get(1.0, tk.END).strip()
        
        if not header_code or not source_code:
            messagebox.showwarning("警告", "请先生成代码")
            return
        
        # 复制头文件和源文件内容到剪贴板
        source_ext = "cpp" if self.selected_language.get() == "C++语言" else "c"
        clipboard_content = f"// 头文件 ({self.selected_peripheral.get().lower()}_driver.h)\n{header_code}\n\n// 源文件 ({self.selected_peripheral.get().lower()}_driver.{source_ext})\n{source_code}"
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_content)
        messagebox.showinfo("提示", "代码已复制到剪贴板")
    
    def on_mcu_change(self, event):
        """当单片机型号改变时的处理"""
        mcu = self.selected_mcu.get()
        if mcu:
            # 更新库函数选择
            libs = self.lib_types.get(mcu, [])
            self.lib_combobox['values'] = libs
            if libs:
                self.selected_lib.set(libs[0])
            else:
                self.selected_lib.set("")
            
            # 更新默认晶振频率
            xtal = self.default_xtal.get(mcu, 16)
            self.xtal_frequency.set(xtal)
            
            # 更新参数预览
            self.update_preview()
    
    def on_peripheral_change(self, event):
        """当外设接口改变时的处理"""
        peripheral = self.selected_peripheral.get()
        if peripheral:
            # 清空参数面板
            for widget in self.param_frame.winfo_children():
                widget.destroy()
            
            # 根据选择的外设生成参数设置面板
            self.create_peripheral_params(peripheral)
            
            # 更新参数预览
            self.update_preview()
    
    def create_peripheral_params(self, peripheral):
        """创建外设参数设置面板"""
        params = self.peripheral_params.get(peripheral, {})
        
        if not params:
            return
        
        # 创建参数表格
        row = 0
        for param_name, param_var in params.items():
            # 美化参数名称
            display_name = param_name.replace("_", " ").title()
            
            # 创建标签
            label = ttk.Label(self.param_frame, text=display_name, font=self.label_font)
            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            
            # 根据参数类型创建不同的控件
            if param_name in ["mode", "level", "pull", "databits", "parity", "stopbits", "flowcontrol", "count_mode", "i2c_mode"]:
                # 下拉选择框
                values = []
                if param_name == "mode":
                    if peripheral == "GPIO":
                        values = ["输入", "输出"]
                    elif peripheral == "I2C":
                        values = ["主模式", "从模式"]
                    elif peripheral == "SPI":
                        values = ["模式0", "模式1", "模式2", "模式3"]
                elif param_name == "level":
                    values = ["高电平", "低电平"]
                elif param_name == "pull":
                    values = ["无", "上拉", "下拉"]
                elif param_name == "databits":
                    values = ["8位", "7位", "9位"]
                elif param_name == "parity":
                    values = ["无校验", "奇校验", "偶校验"]
                elif param_name == "stopbits":
                    values = ["1位", "2位"]
                elif param_name == "flowcontrol":
                    values = ["关闭", "打开"]
                elif param_name == "count_mode":
                    values = ["向上计数", "向下计数", "中心对齐"]
                elif param_name == "i2c_mode":
                    values = ["硬件IIC", "软件模拟IIC"]
                
                combobox = ttk.Combobox(
                    self.param_frame, 
                    textvariable=param_var, 
                    values=values, 
                    state="readonly",
                    width=15
                )
                combobox.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            else:
                # 文本输入框
                entry = ttk.Entry(self.param_frame, textvariable=param_var, width=15)
                entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            
            row += 1
    
    def update_preview(self, *args):
        """更新参数预览"""
        preview = []
        preview.append(f"单片机型号: {self.selected_mcu.get()}")
        preview.append(f"库函数类型: {self.selected_lib.get()}")
        preview.append(f"外部晶振: {self.xtal_frequency.get()} MHz")
        preview.append(f"外设接口: {self.selected_peripheral.get()}")
        preview.append(f"代码语言: {self.selected_language.get()}")
        
        # 添加外设参数
        peripheral = self.selected_peripheral.get()
        if peripheral:
            preview.append("")
            preview.append("外设参数:")
            params = self.peripheral_params.get(peripheral, {})
            for param_name, param_var in params.items():
                display_name = param_name.replace("_", " ").title()
                preview.append(f"  {display_name}: {param_var.get()}")
        
        # 更新预览文本
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "\n".join(preview))
    
    def save_code(self):
        """保存代码到文件"""
        # 获取头文件和源文件内容
        header_code = self.header_text.get(1.0, tk.END).strip()
        source_code = self.source_text.get(1.0, tk.END).strip()
        
        if not header_code or not source_code:
            messagebox.showwarning("警告", "请先生成代码")
            return
        
        # 获取保存路径
        directory = filedialog.askdirectory(title="选择保存文件夹")
        if not directory:
            return
        
        # 获取当前选择的外设和语言
        peripheral = self.selected_peripheral.get()
        language = self.selected_language.get()
        
        # 确定源文件扩展名
        if language == "C++语言":
            source_ext = ".cpp"
        else:
            source_ext = ".c"
        
        # 生成文件名
        header_file = f"{directory}\\{peripheral.lower()}_driver.h"
        source_file = f"{directory}\\{peripheral.lower()}_driver{source_ext}"
        
        try:
            # 保存头文件
            with open(header_file, "w", encoding="utf-8") as f:
                f.write(header_code)
            
            # 保存源文件
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(source_code)
            
            messagebox.showinfo("提示", f"代码已保存到:\n{header_file}\n{source_file}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {str(e)}")

if __name__ == "__main__":
    """主函数"""
    root = tk.Tk()
    app = MCUDriverGenerator(root)
    root.mainloop()