from data_import.process import Processor

if __name__ == '__main__':
    processor = Processor()
    processor.process_all()
    processor.print_stats()