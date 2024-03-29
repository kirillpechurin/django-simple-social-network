from unittest.mock import patch


class MockTestCaseMixin:

    # Запуск мока
    def _mock(self,
              target: str):
        patcher = patch(target)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock
