require 'spec_helper'

describe package('Google Chrome') do
  it { should be_installed }
end


describe 'Проверка наличия и версии Python' do
  it 'Python установлен и имеет нужную версию' do
    command = 'python --version'
    output = command(command)
    expect(output.exit_status).to eq 0
    expect(output.stdout).to match 'Python 3.7.9'
  end
end


describe 'Проверка наличия и версии библиотеки selenium-wire в Python' do
  it 'библиотека selenium-wire установлена и имеет нужную версию' do
    command = 'python -c "import seleniumwire; print(seleniumwire.__version__)"'
    output = command(command)
    expect(output.exit_status).to eq 0
    expect(output.stdout).to match '5.1.0'
  end
end


describe 'Проверка наличия и версии библиотеки requests в Python' do
  it 'библиотека requests установлена и имеет нужную версию' do
    command = 'python -c "import requests; print(requests.__version__)"'
    output = command(command)
    expect(output.exit_status).to eq 0
    expect(output.stdout).to match '2.31.0'
  end
end


describe 'Проверка наличия и версии библиотеки tqdm в Python' do
  it 'библиотека tqdm установлена и имеет нужную версию' do
    command = 'python -c "import tqdm; print(tqdm.__version__)"'
    output = command(command)
    expect(output.exit_status).to eq 0
    expect(output.stdout).to match '4.66.1'
  end
end


describe 'Проверка наличия и версии библиотеки pytest в Python' do
  it 'библиотека pytest установлена и имеет нужную версию' do
    command = 'python -c "import pytest; print(pytest.__version__)"'
    output = command(command)
    expect(output.exit_status).to eq 0
    expect(output.stdout).to match '7.4.2'
  end
end


describe 'Проверка наличия и версии библиотеки pandas в Python' do
  it 'библиотека pandas установлена и имеет нужную версию' do
    command = 'python -c "import pandas; print(pandas.__version__)"'
    output = command(command)
    expect(output.exit_status).to eq 0
    expect(output.stdout).to match '1.3.5'
  end
end
