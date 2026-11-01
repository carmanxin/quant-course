# @quantlab/output: 323940cc
class QuantProcessingScheduler:
    """
    量化策略的数据处理调度器。

    协调批处理和流处理任务的执行。
    """

    def __init__(self):
        self.daily_batch_tasks = []
        self.intraday_stream_tasks = []

    def register_daily_task(self, task_name: str, func, priority: int = 0):
        """
        注册日终批处理任务。

        执行顺序按 priority 升序（数字越小越先执行）。
        """
        self.daily_batch_tasks.append({
            'name': task_name,
            'func': func,
            'priority': priority
        })
        self.daily_batch_tasks.sort(key=lambda x: x['priority'])

    def register_stream_task(self, task_name: str, func):
        """注册实时流处理任务"""
        self.intraday_stream_tasks.append({
            'name': task_name,
            'func': func
        })

    def run_daily_batch(self, date: str):
        """
        运行日终批处理管道。

        典型任务链：
        1. 数据下载和校验
        2. 日频因子计算
        3. 组合估值和风险计算
        4. 策略信号生成
        5. 报告生成
        6. 数据备份
        """
        results = {}
        for task in self.daily_batch_tasks:
            try:
                result = task['func'](date)
                results[task['name']] = 'SUCCESS'
            except Exception as e:
                results[task['name']] = f'FAILED: {str(e)}'
                # 关键任务失败时停止
                if task['priority'] <= 2:
                    raise

        return results
